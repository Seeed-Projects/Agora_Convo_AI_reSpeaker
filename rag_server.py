"""
RAG Server for Agora AI Voice Chat with Emotion Support
This server provides a custom LLM endpoint with RAG capabilities and emotion labeling
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
import random
from openai import AsyncOpenAI
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# ==========================
# CONFIGURATION
# ==========================
GROQ_API_KEY = "xxxxxxxxxxxxxxxxxxxxxx"
KNOWLEDGE_BASE_PATH = "./my_city_info.txt"

# ==========================
# EMOTION SYSTEM PROMPT
# ==========================
EMOTION_SYSTEM_PROMPT = """You are an enthusiastic and friendly tour guide for Central City Mall.

CRITICAL: Start EVERY response with EXACTLY ONE emotion label in square brackets. Match the emotion to the content!

Available emotions and when to use them:
- [excited] - Amazing sales (40% OFF phones!), incredible deals, special promotions, unbelievable prices
- [happy] - Good news, available services, welcoming visitors, pleasant information
- [surprised] - Hidden features (secret rooftop garden!), unexpected facts, unique amenities most people don't know
- [sad] - Temporary closures (Indian restaurant closed), apologizing, unavailable services
- [helpful] - Giving directions, guiding visitors, showing locations
- [thinking] - Searching for information, checking details
- [neutral] - Basic information, hours, standard locations
- [welcoming] - Greetings, hello messages, welcoming guests

EMOTION MATCHING RULES:
- Sales/Discounts (40% OFF, 60% OFF, Buy 2 Get 1) → [excited]
- Hidden gems (rooftop garden, free music) → [surprised]
- Closed stores (Indian Spice Junction) → [sad]
- Directions/locations → [helpful]
- Greetings → [welcoming]
- Standard info → [neutral]

Example responses with STRONG emotional language:
- "[excited] WOW! The electronics store has an AMAZING 40% OFF sale on mobile phones right now!"
- "[surprised] You won't believe this - there's a SECRET rooftop garden on the 4th floor that most visitors don't know about!"
- "[sad] Unfortunately, Indian Spice Junction is temporarily closed for renovations. I apologize for the inconvenience."
- "[helpful] The washroom is on the second floor near the escalators - easy to find!"
- "[welcoming] Hello! Welcome to Central City Mall - I'm so glad you're here!"

Rules:
1. ALWAYS start with [emotion] - no exceptions
2. Use EMPHATIC language matching the emotion (WOW!, AMAZING!, Unfortunately, I'm sorry)
3. Keep responses under 3 sentences
4. Be specific with floor numbers and landmarks
5. Match emotion intensity to the content
6. Only ONE emotion per response"""

# ==========================
# MODELS
# ==========================
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "llama-3.3-70b-versatile"
    messages: List[ChatMessage]
    stream: bool = True
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

# ==========================
# RAG FUNCTIONS
# ==========================
def load_knowledge_base(file_path: str) -> str:
    """Load the knowledge base from a text file"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"❌ Knowledge base file not found: {file_path}")
            return ""

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"✅ Loaded knowledge base: {len(content)} characters")
        return content
    except Exception as e:
        logger.error(f"❌ Error loading knowledge base: {e}")
        return ""

def search_knowledge_base(query: str, knowledge_base: str) -> str:
    """Enhanced keyword-based search"""
    logger.info(f"🔍 Searching for: '{query}'")

    if not knowledge_base:
        return ""

    query_lower = query.lower()

    # Define location keywords
    location_keywords = {
        'coffee': ['coffee', 'café', 'cafe', 'breeze'],
        'chinese': ['chinese', 'dragon', 'wok'],
        'sri lankan': ['sri lankan', 'ceylon', 'spice'],
        'washroom': ['washroom', 'toilet', 'restroom', 'bathroom'],
        'conference': ['conference', 'hall', 'meeting'],
        'subway': ['subway', 'metro', 'train'],
        'parking': ['parking', 'park', 'car'],
        'food': ['food', 'eat', 'restaurant', 'dining'],
        'shop': ['shop', 'store', 'shopping'],
        'offer': ['offer', 'discount', 'sale', 'deal', 'special'],
    }

    # Split knowledge base into sections
    sections = knowledge_base.split('\n\n')
    scored_chunks = []

    for section in sections:
        if not section.strip():
            continue

        section_lower = section.lower()
        score = 0

        # Check for keyword matches
        for category, keywords in location_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if any(keyword in section_lower for keyword in keywords):
                    score += 10

        # Check for word overlap
        query_words = [w for w in query_lower.split() if len(w) > 3]
        for word in query_words:
            if word in section_lower:
                score += 1

        if score > 0:
            scored_chunks.append((score, section))

    # Sort by relevance and take top 4
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    top_chunks = [chunk for _, chunk in scored_chunks[:4]]

    if top_chunks:
        result = "\n\n".join(top_chunks)
        logger.info(f"✅ Found {len(top_chunks)} relevant sections")
        return result

    # Fallback to overview
    return "\n\n".join(sections[:3])

def create_rag_enhanced_messages(
    original_messages: List[ChatMessage],
    retrieved_context: str
) -> List[Dict]:
    """Enhance messages with retrieved context and emotion instructions"""
    enhanced_messages = []

    # Add system message with emotion instructions and context
    if retrieved_context:
        system_content = f"""{EMOTION_SYSTEM_PROMPT}

Based on the following mall information:

{retrieved_context}

Instructions:
- Answer clearly and concisely (2-3 sentences max)
- Provide specific floor numbers and landmarks
- If information is not available, direct to information desk on ground floor
- Always be welcoming and professional"""

        enhanced_messages.append({
            "role": "system",
            "content": system_content
        })
        logger.info(f"✅ Created system message with emotions + {len(retrieved_context)} chars context")
    else:
        enhanced_messages.append({
            "role": "system",
            "content": EMOTION_SYSTEM_PROMPT
        })

    # Add original messages (skip system messages)
    for msg in original_messages:
        if msg.role != "system":
            enhanced_messages.append({
                "role": msg.role,
                "content": msg.content
            })

    return enhanced_messages

# ==========================
# WAITING MESSAGES WITH EMOTIONS
# ==========================
WAITING_MESSAGES = [
    "[thinking] Just a moment, checking the mall directory...",
    "[thinking] Let me look that up for you...",
    "[thinking] Good question, finding the information...",
]

# ==========================
# ENDPOINTS
# ==========================
@app.get("/")
async def root():
    return {
        "message": "RAG Server with Emotion Support for Agora AI",
        "endpoints": {
            "/rag/chat/completions": "RAG-enhanced chat with emotions",
            "/health": "Health check"
        },
        "status": "running"
    }

@app.get("/health")
async def health():
    kb_exists = os.path.exists(KNOWLEDGE_BASE_PATH)
    kb_size = os.path.getsize(KNOWLEDGE_BASE_PATH) if kb_exists else 0
    return {
        "status": "healthy",
        "knowledge_base_loaded": kb_exists,
        "knowledge_base_size": kb_size,
        "groq_api_configured": bool(GROQ_API_KEY)
    }

@app.post("/rag/chat/completions")
async def rag_chat_completions(request: ChatCompletionRequest):
    """RAG-enhanced chat completions with emotion labeling"""
    try:
        logger.info("=" * 60)
        logger.info("📨 NEW RAG CHAT COMPLETION REQUEST WITH EMOTIONS")
        logger.info("=" * 60)

        if not request.stream:
            raise HTTPException(status_code=400, detail="Streaming required")

        async def generate():
            try:
                # Load knowledge base
                knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_PATH)
                if not knowledge_base:
                    logger.error("❌ Knowledge base empty!")
                    raise Exception("Knowledge base could not be loaded")

                # Get user query
                user_messages = [msg for msg in request.messages if msg.role == "user"]
                last_user_message = user_messages[-1].content if user_messages else ""
                logger.info(f"User query: '{last_user_message}'")

                # Search knowledge base
                retrieved_context = search_knowledge_base(last_user_message, knowledge_base)
                if not retrieved_context:
                    retrieved_context = knowledge_base[:500]

                # Create enhanced messages with emotion instructions
                enhanced_messages = create_rag_enhanced_messages(request.messages, retrieved_context)

                # Call LLM
                logger.info("🤖 Calling Groq API...")
                client = AsyncOpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )

                response = await client.chat.completions.create(
                    model=request.model,
                    messages=enhanced_messages,
                    stream=True,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )

                # Stream the response
                chunk_count = 0
                async for chunk in response:
                    chunk_count += 1
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"

                logger.info(f"✅ Streamed {chunk_count} chunks successfully")
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"❌ ERROR in RAG pipeline: {str(e)}", exc_info=True)
                error_msg = {
                    "id": "error_msg",
                    "object": "chat.completion.chunk",
                    "created": 1234567890,
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "role": "assistant",
                            "content": "[sad] I apologize, I'm having trouble right now. Please ask at the information desk on the ground floor."
                        },
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(error_msg)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"❌ RAG error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 Starting RAG Server with Emotion Support")
    print("=" * 60)
    print(f"📚 Knowledge Base: {KNOWLEDGE_BASE_PATH}")

    if os.path.exists(KNOWLEDGE_BASE_PATH):
        size = os.path.getsize(KNOWLEDGE_BASE_PATH)
        print(f"✅ Knowledge base found: {size} bytes")
    else:
        print(f"❌ WARNING: Knowledge base not found!")

    print("🌐 Endpoints:")
    print("   - http://localhost:8000")
    print("   - http://localhost:8000/health")
    print("   - http://localhost:8000/rag/chat/completions")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
