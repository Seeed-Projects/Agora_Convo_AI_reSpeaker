# emotion_led_service.py
"""
Emotion LED Control Service for ReSpeaker
Receives emotion data and controls LED animations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import struct
import time
import threading
from typing import Optional

# Try to import USB libraries
try:
    import usb.core
    import usb.util

    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("⚠️  PyUSB not installed. Install with: pip install pyusb")

try:
    import libusb_package

    LIBUSB_AVAILABLE = True
except ImportError:
    LIBUSB_AVAILABLE = False

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# ReSpeaker LED Control
# ==========================

PARAMETERS = {
    "LED_EFFECT": (20, 12, 1, "rw", "uint8"),
    "LED_BRIGHTNESS": (20, 13, 1, "rw", "uint8"),
    "LED_GAMMIFY": (20, 14, 1, "rw", "uint8"),
    "LED_SPEED": (20, 15, 1, "rw", "uint8"),
    "LED_COLOR": (20, 16, 1, "rw", "uint32"),
}


class ReSpeaker:
    """ReSpeaker USB device controller"""
    TIMEOUT = 100000

    def __init__(self, dev):
        self.dev = dev

    def write(self, name, data_list):
        """Write parameter to device"""
        if name not in PARAMETERS:
            raise ValueError(f"Unknown parameter: {name}")

        data = PARAMETERS[name]
        if len(data_list) != data[2]:
            raise ValueError('{} value count is not {}'.format(name, data[2]))

        windex = data[0]
        wvalue = data[1]
        data_cnt = data[2]
        data_type = data[4]
        payload = []

        if data_type == 'uint8':
            for i in range(data_cnt):
                payload += data_list[i].to_bytes(1, byteorder='little')
        elif data_type == 'uint32':
            for i in range(data_cnt):
                payload += struct.pack(b'I', data_list[i])

        self.dev.ctrl_transfer(
            usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
            0, wvalue, windex, payload, self.TIMEOUT)

    def close(self):
        """Release USB device"""
        try:
            usb.util.dispose_resources(self.dev)
        except:
            pass


def find_device(vid=0x2886, pid=0x001A):
    """Find ReSpeaker USB device"""
    if not USB_AVAILABLE:
        return None

    try:
        if sys.platform.startswith('win') and LIBUSB_AVAILABLE:
            dev = libusb_package.find(idVendor=vid, idProduct=pid)
        else:
            dev = usb.core.find(idVendor=vid, idProduct=pid)

        if not dev:
            return None

        return ReSpeaker(dev)
    except Exception as e:
        print(f"Error finding device: {e}")
        return None


# ==========================
# Emotion to Color Mapping
# ==========================

EMOTION_COLORS = {
    "happy": 0xFFFF00,  # Yellow - Bright and cheerful
    "excited": 0xFF00FF,  # Magenta - Vibrant and energetic
    "surprised": 0xFF8800,  # Orange - Bright surprise
    "thinking": 0x00FFFF,  # Cyan - Cool contemplation
    "helpful": 0x00FF00,  # Green - Friendly assistance
    "neutral": 0x8888FF,  # Light blue - Calm neutral
    "sad": 0x0000FF,  # Blue - Somber
    "welcoming": 0xFF69B4,  # Pink - Warm welcome
    "loving": 0xFF1493,  # Deep pink - Affectionate
    "curious": 0x9932CC,  # Purple - Intrigued
    "angry": 0xFF0000,  # Red - Intense
    "sleepy": 0x4B0082,  # Indigo - Drowsy
}

# LED animation lock to prevent conflicts
led_lock = threading.Lock()


def play_emotion_animation(emotion: str, duration: float = 1.0):
    """
    Play LED animation for detected emotion

    Args:
        emotion: Emotion name (e.g., "happy", "excited")
        duration: Animation duration in seconds (default: 1.0)

    Returns:
        bool: True if successful
    """
    if not USB_AVAILABLE:
        print("⚠️  USB not available")
        return False

    with led_lock:  # Ensure only one animation at a time
        dev = find_device()
        if not dev:
            print("❌ ReSpeaker device not found")
            return False

        try:
            # Get color for emotion (default to cyan if unknown)
            color = EMOTION_COLORS.get(emotion.lower(), 0x00FFFF)

            print(f"🎭 Playing animation for emotion: {emotion} (color: {hex(color)})")

            # Set breathing effect with emotion color
            dev.write("LED_GAMMIFY", [1])  # Smooth effect
            dev.write("LED_EFFECT", [1])  # Breath effect (1 = breathing)
            dev.write("LED_COLOR", [color])  # Emotion color
            dev.write("LED_SPEED", [8])  # Speed (1-20, higher = faster)
            dev.write("LED_BRIGHTNESS", [200])  # Bright

            # Hold the animation
            time.sleep(duration)

            # Return to DoA (Direction of Arrival) mode
            print("🔄 Returning to DoA mode...")
            dev.write("LED_EFFECT", [4])  # DoA mode
            dev.write("LED_BRIGHTNESS", [128])  # Medium brightness

            return True

        except Exception as e:
            print(f"❌ ReSpeaker LED error: {e}")
            return False
        finally:
            dev.close()


# ==========================
# API Models
# ==========================

class EmotionRequest(BaseModel):
    emotion: str
    duration: Optional[float] = 1.0
    text: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    message: str
    usb_available: bool
    device_found: bool


# ==========================
# API Endpoints
# ==========================

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Emotion LED Control Service",
        "status": "running",
        "usb_available": USB_AVAILABLE,
        "endpoints": {
            "/emotion": "POST - Trigger emotion LED animation",
            "/test/{color}": "GET - Test LED with specific color",
            "/status": "GET - Check device status",
            "/doa": "POST - Return to DoA mode"
        }
    }


@app.get("/status")
async def get_status():
    """Check ReSpeaker device status"""
    device_found = False

    if USB_AVAILABLE:
        dev = find_device()
        if dev:
            device_found = True
            dev.close()

    return StatusResponse(
        status="ok" if device_found else "no_device",
        message="Device ready" if device_found else "Device not found",
        usb_available=USB_AVAILABLE,
        device_found=device_found
    )


@app.post("/emotion")
async def trigger_emotion(request: EmotionRequest):
    """
    Trigger LED animation for detected emotion

    Example:
        POST /emotion
        {
            "emotion": "excited",
            "duration": 1.0,
            "text": "WOW! 40% OFF on phones!"
        }
    """
    if not USB_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="USB libraries not available. Install pyusb."
        )

    print(f"\n{'=' * 60}")
    print(f"🎭 Emotion Detected: {request.emotion}")
    if request.text:
        print(f"📝 Text: {request.text}")
    print(f"⏱️  Duration: {request.duration}s")
    print(f"{'=' * 60}\n")

    # Play animation in background thread to avoid blocking
    thread = threading.Thread(
        target=play_emotion_animation,
        args=(request.emotion, request.duration)
    )
    thread.daemon = True
    thread.start()

    return {
        "status": "success",
        "emotion": request.emotion,
        "message": f"Playing {request.emotion} animation"
    }


@app.post("/doa")
async def return_to_doa():
    """Return LED to DoA (Direction of Arrival) mode"""
    if not USB_AVAILABLE:
        raise HTTPException(status_code=503, detail="USB not available")

    with led_lock:
        dev = find_device()
        if not dev:
            raise HTTPException(status_code=404, detail="Device not found")

        try:
            dev.write("LED_EFFECT", [4])  # DoA mode
            dev.write("LED_BRIGHTNESS", [128])
            return {"status": "success", "message": "Returned to DoA mode"}
        finally:
            dev.close()


@app.get("/test/{color}")
async def test_color(color: str):
    """
    Test LED with specific color

    Available colors: red, green, blue, yellow, purple, cyan,
                     magenta, orange, pink, white
    """
    color_map = {
        "red": 0xFF0000,
        "green": 0x00FF00,
        "blue": 0x0000FF,
        "yellow": 0xFFFF00,
        "purple": 0x9932CC,
        "cyan": 0x00FFFF,
        "magenta": 0xFF00FF,
        "orange": 0xFF8800,
        "pink": 0xFF69B4,
        "white": 0xFFFFFF,
    }

    if color.lower() not in color_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown color. Available: {list(color_map.keys())}"
        )

    if not USB_AVAILABLE:
        raise HTTPException(status_code=503, detail="USB not available")

    with led_lock:
        dev = find_device()
        if not dev:
            raise HTTPException(status_code=404, detail="Device not found")

        try:
            color_hex = color_map[color.lower()]
            dev.write("LED_EFFECT", [1])  # Breathing
            dev.write("LED_COLOR", [color_hex])
            dev.write("LED_BRIGHTNESS", [200])
            dev.write("LED_SPEED", [8])

            time.sleep(1.0)

            dev.write("LED_EFFECT", [4])  # Back to DoA
            dev.write("LED_BRIGHTNESS", [128])

            return {
                "status": "success",
                "color": color,
                "hex": hex(color_hex)
            }
        finally:
            dev.close()


# ==========================
# Startup Check
# ==========================

@app.on_event("startup")
async def startup_event():
    """Check device on startup"""
    print("\n" + "=" * 60)
    print("🚀 Emotion LED Control Service Starting...")
    print("=" * 60)

    if not USB_AVAILABLE:
        print("⚠️  WARNING: PyUSB not installed!")
        print("   Install with: pip install pyusb")
        print("   LED control will not work without it.")
    else:
        print("✅ PyUSB available")

        dev = find_device()
        if dev:
            print("✅ ReSpeaker device found!")
            try:
                # Set to DoA mode on startup
                dev.write("LED_EFFECT", [4])
                dev.write("LED_BRIGHTNESS", [128])
                print("✅ Device initialized in DoA mode")
            except Exception as e:
                print(f"⚠️  Device initialization error: {e}")
            finally:
                dev.close()
        else:
            print("⚠️  ReSpeaker device not found")
            print("   Make sure device is connected")

    print("\n🎨 Emotion Color Mapping:")
    for emotion, color in EMOTION_COLORS.items():
        print(f"   {emotion:12s} → {hex(color)}")

    print("\n🌐 Service running on http://localhost:5000")
    print("=" * 60 + "\n")


# ==========================
# Run Server
# ==========================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("🎭 Starting Emotion LED Control Service")
    print("=" * 60)
    print("📡 Port: 5000")
    print("🎨 Endpoints:")
    print("   POST /emotion - Trigger emotion animation")
    print("   GET  /status - Check device status")
    print("   POST /doa - Return to DoA mode")
    print("   GET  /test/{color} - Test LED colors")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")