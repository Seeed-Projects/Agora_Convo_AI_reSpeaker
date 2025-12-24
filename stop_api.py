# stop_api.py
# Stop the conversational AI agent

import base64
import requests
import sys
from config import CUSTOMER_KEY, CUSTOMER_SECRET, APP_ID

# ==========================
# AGENT ID (Update this!)
# ==========================
# Copy the agent_id from join_api.py output
AGENT_ID = "A42AC47HM54EV67MM93MC94VN86NR36T"

# ==========================
# Base64 encode credentials
# ==========================
raw = f"{CUSTOMER_KEY}:{CUSTOMER_SECRET}"
BASIC = base64.b64encode(raw.encode()).decode()

# ==========================
# Stop Agent URL
# ==========================
url = f"https://api.agora.io/api/conversational-ai-agent/v2/projects/{APP_ID}/agents/{AGENT_ID}/leave"

headers = {
    "Authorization": f"Basic {BASIC}",
    "Content-Type": "application/json"
}

# ==========================
# Validation
# ==========================
if AGENT_ID == "YOUR_AGENT_ID_HERE":
    print("=" * 50)
    print("❌ ERROR: Please update AGENT_ID first!")
    print("=" * 50)
    print("\n📝 Steps:")
    print("1. Run join_api.py")
    print("2. Copy the agent_id from the output")
    print("3. Paste it in stop_api.py (line 11)")
    print("4. Run stop_api.py again")
    print("=" * 50)
    sys.exit(1)

# ==========================
# SEND REQUEST
# ==========================
print("=" * 50)
print("🛑 Stopping AI Agent...")
print("=" * 50)
print(f"Agent ID: {AGENT_ID}")
print("=" * 50)

response = requests.post(url, headers=headers)

print("\n📊 Response:")
print("-" * 50)
print("Status Code:", response.status_code)

if response.status_code == 200:
    print("\n✅ SUCCESS!")
    print("Agent stopped and left the channel")
else:
    print("\n❌ FAILED!")
    try:
        print("Error:", response.json())
    except:
        print("Error:", response.text)

print("\n" + "=" * 50)