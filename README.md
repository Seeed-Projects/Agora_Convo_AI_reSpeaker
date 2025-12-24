# 🎭 AI Voice Assistant with Emotion Detection & LED Control

A real-time conversational AI assistant powered by Agora, with RAG (Retrieval-Augmented Generation), emotion detection, live transcripts, and ReSpeaker LED visualization.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🎙️ **Real-time Voice Conversation** - Talk naturally with AI assistant
- 🤖 **RAG-Powered Responses** - Custom knowledge base for accurate answers
- 🎭 **Emotion Detection** - AI responses include emotional context
- 💡 **LED Visualization** - ReSpeaker lights up with emotion colors
- 📝 **Live Transcripts** - Real-time conversation transcription
- 🌐 **Web Interface** - Beautiful, animated UI
- 🔊 **Voice Synthesis** - Natural-sounding TTS responses

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Agora Account Setup](#1-agora-account-setup)
  - [2. Third-Party API Keys](#2-third-party-api-keys)
  - [3. Generate Tokens](#3-generate-tokens)
  - [4. Configure Project](#4-configure-project)
  - [5. Setup RAG Server](#5-setup-rag-server)
  - [6. Setup LED Control (Optional)](#6-setup-led-control-optional)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

---

## 🔧 Prerequisites

### Required Hardware
- Computer with reSpeaker (built-in or external)
- Internet connection


### Required Software
- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge)

### Required Accounts
- [Agora Account](https://console.agora.io/)
- [AssemblyAI Account](https://www.assemblyai.com/) (for speech recognition)
- [Groq Account](https://groq.com/) (for LLM and TTS)

---

## 🚀 Setup Instructions

### 1. Agora Account Setup

#### Step 1.1: Create Agora Account
1. Go to [Agora Console](https://console.agora.io/)
2. Sign up for a free account
3. Verify your email

#### Step 1.2: Create a Project
1. In the Agora Console, click **"Create Project"**
2. Enter a project name (e.g., "AI Voice Assistant")
3. Choose **"Secured mode: APP ID + Token"**
4. Click **"Create"**

#### Step 1.3: Get Your Credentials
After creating the project, you'll see:
- **APP ID** - Copy this (looks like: `550749b706214846a1a2eef3612a8cd3`)
- Click **"Configure"** next to your project
- Find **"Primary Certificate"** - Copy this

#### Step 1.4: Get Customer Key & Customer Secret
1. In Agora Console, go to [RESTful API](https://console.agora.io/restful)
2. Click **"Add a secret"** or view existing secrets
3. Copy:
   - **Customer Key** (looks like: `8a598f4690f740c9a8760a10e28cae9d`)
   - **Customer Secret** (looks like: `0706c45e30b74b7fa4b3c71eae2c2924`)

📚 **Reference**: [Agora RESTful Authentication Guide](https://docs.agora.io/en/conversational-ai/rest-api/restful-authentication)

---

### 2. Third-Party API Keys

#### Step 2.1: Get AssemblyAI API Key
1. Go to [AssemblyAI](https://www.assemblyai.com/)
2. Sign up for a free account
3. Go to your [Dashboard](https://www.assemblyai.com/app)
4. Copy your **API Key**

#### Step 2.2: Get Groq API Keys
1. Go to [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to [API Keys](https://console.groq.com/keys)
4. Create **two API keys**:
   - One for LLM (text generation)
   - One for TTS (text-to-speech)
5. Copy both keys

---

### 3. Generate Tokens

#### Step 3.1: Clone Token Generator
```bash
git clone https://github.com/KasunThushara/RTM_RTC_TokenGenerator.git
cd RTM_RTC_TokenGenerator
```

#### Step 3.2: Configure Token Generator
Edit the token generator configuration with your Agora credentials:
```python
# In the token generator script
APP_ID = "your_app_id_from_step_1.3"
APP_CERTIFICATE = "your_primary_certificate_from_step_1.3"
```

#### Step 3.3: Generate Token for Agent (UID: 1001)
```bash
python generate_rtc_rtm_token.py --account 1001
```

**Copy the generated token** - This is for the AI Agent
```
Token: 007eJxTYHhx+deOGjf+P58sJG4e...
```

#### Step 3.4: Generate Token for User (UID: 1002)
```bash
python generate_rtc_rtm_token.py --account 1002
```

**Copy the generated token** - This is for the Web User

⚠️ **Important**: Keep both tokens safe. You'll need them in the next steps.

---

### 4. Configure Project

#### Step 4.1: Clone This Repository
```bash
git clone https://github.com/KasunThushara/Agora_Convo_AI_reSpeaker.git
cd ai-voice-assistant
```

#### Step 4.2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install manually:
```bash
pip install fastapi uvicorn requests openai pydantic
```

#### Step 4.3: Configure `config.py`
Create or edit `config.py` with your credentials:

```python
# config.py
# Central configuration file for Agora AI Voice Chat

# ==========================
# AGORA CREDENTIALS
# ==========================
CUSTOMER_KEY = "your_customer_key_from_step_1.4"
CUSTOMER_SECRET = "your_customer_secret_from_step_1.4"
APP_ID = "your_app_id_from_step_1.3"

# ==========================
# CHANNEL SETTINGS
# ==========================
CHANNEL_NAME = "test"
AGORA_TEMP_TOKEN = "your_agent_token_from_step_3.3_uid_1001"

# Agent and User UIDs
AGENT_RTC_UID = "1001"
USER_RTC_UID = "1002"

# ==========================
# 3RD PARTY SERVICES
# ==========================
ASSEMBLY_AI_KEY = "your_assemblyai_key_from_step_2.1"
GROQ_KEY = "your_groq_llm_key_from_step_2.2"
TTS_GROQ_KEY = "your_groq_tts_key_from_step_2.2"

# ==========================
# AGENT SETTINGS
# ==========================
IDLE_TIMEOUT = 120
MAX_HISTORY = 32

SYSTEM_PROMPT = "You are a helpful chatbot."
GREETING_MESSAGE = "Hello, how can I assist you?"
FAILURE_MESSAGE = "Please hold on a second."

LLM_MODEL = "llama-3.3-70b-versatile"
TTS_MODEL = "playai-tts"
TTS_VOICE = "Arista-PlayAI"
ASR_LANGUAGE = "en-US"
```

#### Step 4.4: Configure Web Interface
Edit `index_v5.html` (or your HTML file) in **two places**:

**Location 1: RTM Login Token (around line 950)**
```javascript
// Find this line:
await rtmClient.login();

// Replace with:
await rtmClient.login({token: 'your_user_token_from_step_3.4_uid_1002'});
```

**Location 2: Configuration Panel Inputs**
Update the default values in the HTML:
```html
<!-- App ID -->
<input type="text" class="config-input" id="appId" value="your_app_id">

<!-- Token -->
<input type="text" class="config-input" id="token" value="your_user_token_uid_1002">
```

---

### 5. Setup RAG Server

#### Step 5.1: Customize Knowledge Base
Edit `my_city_info.txt` with your own information:

```text
# Example: Replace with your use case
Your Company/Location Information

Ground Floor
- Main entrance and reception
- Coffee shop location
- Facilities

... (customize with your data)
```

💡 **Use Cases**:
- Shopping mall guide
- Office building directory
- Museum tour guide
- Hotel concierge
- Campus navigation

#### Step 5.2: Test RAG Server Locally
```bash
python rag_server.py
```

You should see:
```
🚀 Starting RAG Server with Emotion Support
✅ Knowledge base found: X bytes
🌐 Service running on http://localhost:8000
```

Test it:
```bash
curl http://localhost:8000/health
```

#### Step 5.3: Setup ngrok (For Cloud Connectivity)

**Why ngrok?** Agora's servers need to reach your RAG server. ngrok creates a public URL.

1. **Install ngrok**:
   - Download from [ngrok.com](https://ngrok.com/download)
   - Or: `brew install ngrok` (Mac) / `choco install ngrok` (Windows)

2. **Sign up and authenticate**:
   ```bash
   ngrok config add-authtoken <your-auth-token>
   ```

3. **Start ngrok tunnel**:
   ```bash
   ngrok http 8000
   ```

4. **Copy the public URL**:
   ```
   Forwarding   https://abcd1234.ngrok-free.app -> http://localhost:8000
   ```

5. **Update `join_api.py`**:
   ```python
   RAG_SERVER_URL = "https://your-ngrok-url.ngrok-free.app/rag/chat/completions"
   USE_RAG = True
   ```

⚠️ **Note**: Free ngrok URLs change each restart. Use a static domain with paid plans.

---

### 6. Setup LED Control (Optional)

Only needed if you have a ReSpeaker USB Microphone.

#### Step 6.1: Install USB Libraries

**Windows**:
```bash
pip install pyusb libusb-package
```

**macOS**:
```bash
brew install libusb
pip install pyusb
```

**Linux**:
```bash
sudo apt-get install libusb-1.0-0-dev
pip install pyusb
```

#### Step 6.2: Test Device Connection
```bash
python test_respeaker.py
```

Expected output:
```
✅ ReSpeaker device found!
   Vendor ID: 0x2886
   Product ID: 0x001a
```

#### Step 6.3: Linux USB Permissions (if needed)
```bash
sudo nano /etc/udev/rules.d/99-respeaker.rules
```

Add this line:
```
SUBSYSTEM=="usb", ATTR{idVendor}=="2886", ATTR{idProduct}=="001a", MODE="0666"
```

Reload rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### Step 6.4: Test LED Service
```bash
python emotion_led_service.py
```

Test all emotions:
```bash
python test_led_emotions.py
```

---

## ▶️ Running the Application

### Terminal Setup

You'll need **4 terminals** (or 3 if skipping LED):

#### Terminal 1: LED Service (Optional)
```bash
python emotion_led_service.py
```

Wait for:
```
✅ ReSpeaker device found!
✅ Device initialized in DoA mode
🌐 Service running on http://localhost:5000
```

#### Terminal 2: RAG Server (with ngrok)
```bash
# Terminal 2a: Start RAG Server
python rag_server.py
```

```bash
# Terminal 2b: Start ngrok (separate terminal/tab)
ngrok http 8000
```

Copy the ngrok URL and update `join_api.py`.

#### Terminal 3: Agora AI Agent
```bash
python join_api.py
```

Wait for:
```
✅ SUCCESS!
Agent ID: A42AA74LL69CF58MN33AE74ME57KJ86K
⚠️  SAVE THIS AGENT ID FOR STOPPING
```

**⚠️ Important**: Copy the Agent ID - you'll need it to stop the agent later.

#### Terminal 4: Open Web Interface
Simply open `index_v5.html` in your web browser.

Or use a local server:
```bash
python -m http.server 8080
# Then visit: http://localhost:8080/index_v5.html
```

### Using the Application

1. **Click "▶ Start Conversation"**
2. **Allow microphone access** when prompted
3. **Start talking!** Try:
   - "Hello!"
   - "Are there any special offers?"
   - "Where is the washroom?"
   - "What are some hidden features?"

4. **Watch the magic happen**:
   - 🎙️ Your speech is transcribed
   - 🤖 AI responds with emotion
   - 📝 Transcripts appear in left panel
   - 🎭 Emoji displays at top
   - 💡 ReSpeaker LEDs light up (if connected)

### Stopping the Application

1. **Stop the conversation**: Click "⏹ Stop Conversation" in web UI

2. **Stop the Agora Agent**:
   ```bash
   # Edit stop_api.py with your Agent ID
   AGENT_ID = "your_agent_id_from_terminal_3"
   
   # Then run:
   python stop_api.py
   ```

3. **Stop other services**: Press `Ctrl+C` in each terminal

---

## 📁 Project Structure

```
ai-voice-assistant/
├── config.py                    # Main configuration file
├── join_api.py                  # Starts Agora AI agent
├── stop_api.py                  # Stops Agora AI agent
├── rag_server.py                # RAG server with emotions
├── emotion_led_service.py       # LED control service
├── my_city_info.txt            # Your knowledge base
├── index.html               # Web interface
├── agora-rtm-2.2.3.min.js      # Agora RTM SDK
├── test_respeaker.py           # Device connection test
├── utils
└── requirements.txt            # Python dependencies
└── index.ts
└── type.ts
```

---

## 🧪 Testing

### Test RAG Server
```bash
# Health check
curl http://localhost:8000/health

# Test query
curl -X POST http://localhost:8000/rag/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Where is the coffee shop?"}],
    "stream": false
  }'
```

### Test LED Control
```bash
# Check device status
curl http://localhost:5000/status

# Test emotion
curl -X POST http://localhost:5000/emotion \
  -H "Content-Type: application/json" \
  -d '{"emotion": "excited", "duration": 1.0}'

# Test color
curl http://localhost:5000/test/yellow
```

### Test End-to-End
1. Start all services
2. Open web interface
3. Start conversation
4. Say: "Are there any special offers?"
5. Verify:
   - ✅ Transcript appears
   - ✅ Emotion emoji shows
   - ✅ LED lights up (if connected)

---

## 🐛 Troubleshooting

### Issue: "Device Not Found"

**ReSpeaker LED**:
```bash
# Check device connection
lsusb | grep 2886  # Linux/Mac
# or check Device Manager (Windows)

# Verify with test script
python test_respeaker.py
```

### Issue: "Agent Join Failed"

**Check**:
1. Verify all credentials in `config.py`
2. Ensure tokens are not expired (regenerate if needed)
3. Check Agora Console for account status
4. Verify network connectivity

**Debug**:
```bash
python join_api.py
# Check the error message in output
```

### Issue: "RAG Server Connection Failed"

**Check**:
1. Is `rag_server.py` running? Check Terminal 2
2. Is ngrok running? Check the public URL
3. Did you update `join_api.py` with ngrok URL?

**Test**:
```bash
# Test local
curl http://localhost:8000/health

# Test ngrok
curl https://your-ngrok-url.ngrok-free.app/health
```

### Issue: "No Transcripts Appearing"

**Check**:
1. Open browser console (F12)
2. Look for RTM connection messages
3. Verify token in `index_v5.html` (UID 1002)
4. Check if `enable_rtm: True` in `join_api.py`

### Issue: "Emotions Not Detected"

**Check**:
1. System prompt includes emotion instructions
2. RAG server has `EMOTION_SYSTEM_PROMPT`
3. Look for `[emotion]` labels in transcripts
4. Check browser console for emotion detection logs

### Issue: "Port Already in Use"

```bash
# Find process using port
lsof -i :5000  # LED service
lsof -i :8000  # RAG server

# Kill process
kill -9 <PID>
```

### Issue: "LED Not Responding"

1. Unplug and replug ReSpeaker
2. Restart LED service
3. Manual reset:
   ```bash
   curl -X POST http://localhost:5000/doa
   ```

---

## 🎨 Emotion Color Reference

| Emotion | Color | Hex | Use Case |
|---------|-------|-----|----------|
| 😊 happy | Yellow | `0xFFFF00` | Good news, positive responses |
| 🎉 excited | Magenta | `0xFF00FF` | Sales, special offers, amazing deals |
| 😲 surprised | Orange | `0xFF8800` | Unexpected facts, hidden features |
| 🤔 thinking | Cyan | `0x00FFFF` | Processing, searching information |
| 🙋 helpful | Green | `0x00FF00` | Giving directions, assistance |
| 😐 neutral | Light Blue | `0x8888FF` | Standard information, facts |
| 😔 sad | Blue | `0x0000FF` | Apologies, closures, bad news |
| 👋 welcoming | Pink | `0xFF69B4` | Greetings, warm welcomes |

---

## 📊 API Reference

### RAG Server (`http://localhost:8000`)

#### `POST /rag/chat/completions`
Generate AI response with RAG

**Request**:
```json
{
  "model": "llama-3.3-70b-versatile",
  "messages": [
    {"role": "user", "content": "Where is the coffee shop?"}
  ],
  "stream": true
}
```

#### `GET /health`
Check server health

**Response**:
```json
{
  "status": "healthy",
  "knowledge_base_loaded": true,
  "knowledge_base_size": 12345
}
```

### LED Service (`http://localhost:5000`)

#### `POST /emotion`
Trigger emotion LED animation

**Request**:
```json
{
  "emotion": "excited",
  "duration": 1.0,
  "text": "Optional transcript"
}
```

#### `GET /status`
Check device status

#### `POST /doa`
Return to Direction of Arrival mode

#### `GET /test/{color}`
Test specific color (red, green, blue, yellow, etc.)

---

## 🔐 Security Notes

⚠️ **Important Security Considerations**:

1. **Never commit credentials to Git**:
   ```bash
   # Add to .gitignore
   config.py
   .env
   *.key
   ```

2. **Use environment variables**:
   ```python
   import os
   GROQ_KEY = os.getenv('GROQ_API_KEY')
   ```

3. **Rotate tokens regularly**: Agora tokens expire after 24 hours by default

4. **Secure ngrok tunnels**: Use authentication for production

5. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [Agora](https://www.agora.io/) - Real-time communication platform
- [Groq](https://groq.com/) - Fast LLM inference
- [AssemblyAI](https://www.assemblyai.com/) - Speech recognition
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [ReSpeaker](https://www.seeedstudio.com/) - Smart microphone

---

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review console logs from all services
3. Verify all credentials are correct
4. Check that all services are running
5. Open an issue on GitHub with:
   - Error messages
   - Steps to reproduce
   - System information

---

## 🎯 Quick Start Checklist

- [ ] Agora account created
- [ ] APP_ID and certificates obtained
- [ ] Customer Key & Secret obtained
- [ ] AssemblyAI API key obtained
- [ ] Groq API keys obtained (LLM + TTS)
- [ ] Tokens generated (UID 1001 & 1002)
- [ ] `config.py` configured
- [ ] `index_v5.html` token updated
- [ ] `my_city_info.txt` customized
- [ ] Python dependencies installed
- [ ] ngrok installed and authenticated
- [ ] All services started
- [ ] Web interface opened
- [ ] Test conversation successful

---

**Ready to go? Start with [Setup Instructions](#setup-instructions)!** 🚀
