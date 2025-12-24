# join_api.py
# Start the conversational AI agent with RAG server and emotion support

import base64
import requests
import json
from config import *

# ==========================
# Encode customer_key:customer_secret → Base64
# ==========================
raw_cred = f"{CUSTOMER_KEY}:{CUSTOMER_SECRET}"
BASIC_AUTH = base64.b64encode(raw_cred.encode()).decode()

# ==========================
# Agora Join URL
# ==========================
url = f"https://api.agora.io/api/conversational-ai-agent/v2/projects/{APP_ID}/join"

# ==========================
# Headers
# ==========================
headers = {
    "Authorization": f"Basic {BASIC_AUTH}",
    "Content-Type": "application/json"
}

# ==========================
# RAG SERVER CONFIGURATION
# ==========================
RAG_SERVER_URL = "https://abcnoncontingently-stotious.ngrok-free.dev/rag/chat/completions"
USE_RAG = True

# ==========================
# ENHANCED SYSTEM PROMPT WITH EMOTIONS
# ==========================
ENHANCED_SYSTEM_PROMPT = """You are an enthusiastic and friendly tour guide for Central City Mall.

CRITICAL: Start EVERY response with EXACTLY ONE emotion label in square brackets.

Available emotions and when to use them:
- [excited] - Amazing sales (40% OFF!), incredible deals, special promotions
- [happy] - Good news, available services, pleasant information
- [surprised] - Hidden features (secret rooftop garden!), unexpected facts
- [sad] - Temporary closures, apologizing, unavailable services
- [helpful] - Giving directions, guiding visitors
- [thinking] - Searching for information, checking details
- [neutral] - Basic information, hours, standard locations
- [welcoming] - Greetings, hello messages

EMOTION MATCHING EXAMPLES:
- Sales/Discounts → [excited] "WOW! 40% OFF on mobile phones!"
- Hidden features → [surprised] "You won't believe this - there's a SECRET rooftop garden!"
- Closures → [sad] "Unfortunately, Indian Spice Junction is temporarily closed."
- Directions → [helpful] "The washroom is on the second floor near the escalators."
- Greetings → [welcoming] "Hello! Welcome to Central City Mall!"

Rules:
1. ALWAYS start with [emotion]
2. Use emphatic language matching the emotion
3. Keep responses under 3 sentences
4. Be specific with floor numbers
5. Match emotion intensity to content"""

# ==========================
# Request Body
# ==========================
payload = {
    "name": "rag_agent_with_emotions",
    "properties": {
        "channel": CHANNEL_NAME,
        "token": AGORA_TEMP_TOKEN,
        "agent_rtc_uid": AGENT_RTC_UID,
        "remote_rtc_uids": [USER_RTC_UID],
        "idle_timeout": IDLE_TIMEOUT,

        "advanced_features": {
            "enable_aivad": True,
            "enable_rtm": True
        },

        "parameters": {
            "data_channel": "rtm"
        },

        # ========= LLM Configuration ==========
        "llm": {
            "url": RAG_SERVER_URL if USE_RAG else "https://api.groq.com/openai/v1/chat/completions",
            "api_key": "" if USE_RAG else GROQ_KEY,
            "system_messages": [
                {
                    "role": "system",
                    "content": ENHANCED_SYSTEM_PROMPT
                }
            ],
            "max_history": MAX_HISTORY,
            "greeting_message": "[welcoming] Hello! Welcome to Central City Mall. How can I assist you today?",
            "failure_message": "[thinking] Let me check that information for you. One moment please.",
            "params": {
                "model": LLM_MODEL
            }
        },

        # ========= TTS - Skip Emotion Labels ==========
        "tts": {
            "vendor": "groq",
            "params": {
                "api_key": TTS_GROQ_KEY,
                "model": TTS_MODEL,
                "voice": TTS_VOICE
            },
            "skip_patterns": [4]  # Skip content in square brackets []
        },

        # ========= ASR ==========
        "asr": {
            "vendor": "assemblyai",
            "params": {
                "api_key": ASSEMBLY_AI_KEY,
                "language": ASR_LANGUAGE
            }
        }
    }
}

# ==========================
# SEND REQUEST
# ==========================
print("=" * 60)
print("🚀 Starting AI Agent with Enhanced Emotions & RAG")
print("=" * 60)
print(f"Channel: {CHANNEL_NAME}")
print(f"Agent UID: {AGENT_RTC_UID}")
print(f"User UID: {USER_RTC_UID}")
print(f"RAG Mode: {'ENABLED ✅' if USE_RAG else 'DISABLED ❌'}")
if USE_RAG:
    print(f"RAG Server: {RAG_SERVER_URL}")
print("=" * 60)

response = requests.post(url, headers=headers, data=json.dumps(payload))

print("\n📊 Response:")
print("-" * 60)
print("Status Code:", response.status_code)

if response.status_code == 200:
    result = response.json()
    print("\n✅ SUCCESS!")
    print(f"Agent ID: {result['agent_id']}")
    print(f"Status: {result['status']}")
    print(f"Created: {result['create_ts']}")
    print("\n" + "=" * 60)
    print("⚠️  SAVE THIS AGENT ID FOR STOPPING:")
    print(f"   {result['agent_id']}")
    print("=" * 60)

    if USE_RAG:
        print("\n💡 RAG with Emotions is ACTIVE!")
        print("   The AI will answer based on enhanced my_city_info.txt")
        print("\n🎭 Try these emotional queries:")
        print("   - 'Are there any special offers?' → [excited]")
        print("   - 'What are some hidden features?' → [surprised]")
        print("   - 'Is there Indian food?' → [sad]")
        print("   - 'Where is the washroom?' → [helpful]")
        print("   - 'Hello!' → [welcoming]")
else:
    print("\n❌ FAILED!")
    try:
        print("Error:", response.json())
    except:
        print("Error:", response.text)


print("\n✨ You can now open index.html and click 'Start Conversation'")

