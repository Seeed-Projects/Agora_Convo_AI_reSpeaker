#!/usr/bin/env python3
"""
Test script for ReSpeaker LED Emotion Control
Tests all emotions with their corresponding colors
"""

import requests
import time
import sys

LED_SERVICE_URL = "http://localhost:5000"

# Emotion test scenarios
TEST_SCENARIOS = [
    {
        "emotion": "welcoming",
        "description": "Pink breathing - Warm welcome",
        "example": "Hello! Welcome to Central City Mall!"
    },
    {
        "emotion": "excited",
        "description": "Magenta breathing - Vibrant energy",
        "example": "WOW! 40% OFF on mobile phones!"
    },
    {
        "emotion": "surprised",
        "description": "Orange breathing - Bright surprise",
        "example": "You won't believe this - there's a SECRET rooftop garden!"
    },
    {
        "emotion": "helpful",
        "description": "Green breathing - Friendly assistance",
        "example": "The washroom is on the second floor near the escalators."
    },
    {
        "emotion": "thinking",
        "description": "Cyan breathing - Cool contemplation",
        "example": "Let me check that information for you..."
    },
    {
        "emotion": "happy",
        "description": "Yellow breathing - Bright and cheerful",
        "example": "Coffee Breeze Café is on the ground floor!"
    },
    {
        "emotion": "sad",
        "description": "Blue breathing - Somber",
        "example": "Unfortunately, Indian Spice Junction is temporarily closed."
    },
    {
        "emotion": "neutral",
        "description": "Light blue breathing - Calm neutral",
        "example": "The mall is open from 9:00 AM to 9:00 PM."
    }
]


def check_service():
    """Check if LED service is running"""
    try:
        response = requests.get(f"{LED_SERVICE_URL}/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get("device_found"):
                print("✅ LED service is running")
                print(f"✅ ReSpeaker device found")
                return True
            else:
                print("❌ LED service running but device not found")
                return False
        else:
            print("❌ LED service returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to LED service")
        print(f"   Make sure emotion_led_service.py is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_emotion(emotion, description, example):
    """Test a specific emotion"""
    print(f"\n{'='*70}")
    print(f"🎭 Testing: {emotion.upper()}")
    print(f"📝 Description: {description}")
    print(f"💬 Example: \"{example}\"")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            f"{LED_SERVICE_URL}/emotion",
            json={
                "emotion": emotion,
                "duration": 1.5,  # Slightly longer for demo
                "text": example
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"💡 Watch the LED breathe in {emotion} color...")
            time.sleep(2.0)  # Wait for animation + return to DoA
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_return_to_doa():
    """Test returning to DoA mode"""
    print(f"\n{'='*70}")
    print("🔄 Testing: Return to DoA Mode")
    print(f"{'='*70}")
    
    try:
        response = requests.post(f"{LED_SERVICE_URL}/doa", timeout=2)
        if response.status_code == 200:
            print("✅ Successfully returned to DoA mode")
            return True
        else:
            print("❌ Failed to return to DoA mode")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("🎭 ReSpeaker LED Emotion Control Test")
    print("="*70)
    
    # Check service
    print("\n📡 Checking LED service...")
    if not check_service():
        print("\n❌ LED service check failed!")
        print("\n📋 To start the LED service:")
        print("   python emotion_led_service.py")
        sys.exit(1)
    
    # Wait a moment
    time.sleep(1)
    
    # Test each emotion
    print("\n🎨 Testing all emotions...")
    print("💡 Watch the ReSpeaker LED ring!\n")
    
    success_count = 0
    for scenario in TEST_SCENARIOS:
        if test_emotion(
            scenario["emotion"],
            scenario["description"],
            scenario["example"]
        ):
            success_count += 1
        time.sleep(0.5)  # Brief pause between tests
    
    # Return to DoA mode
    test_return_to_doa()
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    print(f"✅ Successful: {success_count}/{len(TEST_SCENARIOS)}")
    print(f"❌ Failed: {len(TEST_SCENARIOS) - success_count}/{len(TEST_SCENARIOS)}")
    
    if success_count == len(TEST_SCENARIOS):
        print("\n🎉 All tests passed! LED emotion control is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Check the LED service logs.")
    
    print("\n💡 The LED should now be in DoA mode (rotating directional indicator)")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        print("🔄 Returning to DoA mode...")
        try:
            requests.post(f"{LED_SERVICE_URL}/doa", timeout=2)
        except:
            pass
        sys.exit(0)
