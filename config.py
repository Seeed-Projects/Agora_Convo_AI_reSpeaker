# config.py
# Central configuration file for Agora AI Voice Chat

# ==========================
# AGORA CREDENTIALS
# ==========================
CUSTOMER_KEY = "xxxxxxxxxxxx"
CUSTOMER_SECRET = "xxxxxxxxxx"
APP_ID = "xxxxxxxxxxxx"

# ==========================
# CHANNEL SETTINGS
# ==========================
CHANNEL_NAME = "test"
AGORA_TEMP_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Agent and User UIDs
AGENT_RTC_UID = "1001"
USER_RTC_UID = "1002"

# ==========================
# 3RD PARTY SERVICES
# ==========================
ASSEMBLY_AI_KEY = "xxxxxxxxxxxxx"
GROQ_KEY = "xxxxxxxxxxxxxxxx"
TTS_GROQ_KEY = "xxxxxxxxxxxxxxxxxx"

# ==========================
# AGENT SETTINGS
# ==========================
IDLE_TIMEOUT = 120  # seconds
MAX_HISTORY = 32

# System prompt for the AI
SYSTEM_PROMPT = "You are a helpful chatbot."
GREETING_MESSAGE = "Hello, how can I assist you?"
FAILURE_MESSAGE = "Please hold on a second."

# LLM Model
LLM_MODEL = "llama-3.3-70b-versatile"

# TTS Voice
TTS_MODEL = "playai-tts"
TTS_VOICE = "Arista-PlayAI"

# ASR Language
ASR_LANGUAGE = "en-US"
