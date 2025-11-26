# Bedtime Story Configuration
# Edit these settings to change defaults for your iOS Shortcut

# Default voice for bedtime stories
# See full list: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
# DEFAULT_VOICE = "en-US-AriaNeural"  # Expressive female voice with style support
DEFAULT_VOICE = "en-US-GuyNeural"  # Male voice - great for Bible stories & narration

# Optional: Set a default speaking style
# Available styles depend on the voice - see below
# Set to None to use normal speaking style
# DEFAULT_STYLE = "friendly"  # Best for bedtime - warm, calm, soothing
DEFAULT_STYLE = "hopeful"  # Best for Bible stories - warm, positive, faith-filled tone

# Audio quality settings
OUTPUT_FORMAT = "audio-24khz-96kbitrate-mono-mp3"  # Good balance of quality and file size
# Other options:
# - "audio-48khz-192kbitrate-mono-mp3" (highest quality, larger files)
# - "audio-16khz-32kbitrate-mono-mp3" (smaller files, lower quality)

# Pre-signed URL expiration (hours)
SAS_URL_EXPIRY_HOURS = 48  # How long the download link stays valid

# Synthesis job retention (hours)
SYNTHESIS_TTL_HOURS = 24  # How long Azure keeps the synthesis job

# ==========================================
# Voice + Style Combinations
# ==========================================

# Voices with Multiple Styles (Best for Stories):
VOICE_STYLES = {
    "en-US-AriaNeural": [
        "angry", "cheerful", "excited", "friendly", "hopeful", 
        "sad", "shouting", "terrified", "unfriendly", "whispering"
    ],
    "en-US-DavisNeural": [
        "angry", "cheerful", "excited", "friendly", "hopeful",
        "sad", "shouting", "terrified", "unfriendly", "whispering"
    ],
    "en-US-GuyNeural": [
        "angry", "cheerful", "excited", "friendly", "hopeful",
        "newscast", "sad", "shouting", "terrified", "unfriendly", "whispering"
    ],
    "en-US-JennyNeural": [
        "angry", "assistant", "chat", "cheerful", "customerservice",
        "excited", "friendly", "hopeful", "newscast", "sad", "shouting",
        "terrified", "unfriendly", "whispering"
    ],
    "en-US-SaraNeural": [
        "angry", "cheerful", "excited", "friendly", "hopeful",
        "sad", "shouting", "terrified", "unfriendly", "whispering"
    ]
}

# Recommended Settings for Different Story Types:
STORY_PRESETS = {
    "bedtime": {
        "voice": "en-US-JennyNeural",
        "style": None  # Calm, soothing default
    },
    "adventure": {
        "voice": "en-US-DavisNeural",
        "style": "excited"
    },
    "gentle": {
        "voice": "en-US-AriaNeural",
        "style": "friendly"
    },
    "cheerful": {
        "voice": "en-US-SaraNeural",
        "style": "cheerful"
    }
}

# ==========================================
# Custom Voice Support
# ==========================================

# If you train a custom neural voice, set it here:
CUSTOM_VOICE_NAME = None  # Example: "MyCustomVoice"
CUSTOM_VOICE_DEPLOYMENT_ID = None  # Get this from Azure Speech Studio

# To use custom voice:
# 1. Train voice in Azure Speech Studio
# 2. Deploy the voice
# 3. Set CUSTOM_VOICE_NAME and CUSTOM_VOICE_DEPLOYMENT_ID above
# 4. Change DEFAULT_VOICE to your custom voice name
