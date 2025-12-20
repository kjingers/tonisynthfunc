# Bedtime Story Configuration
# Edit these settings to change defaults for your iOS Shortcut

# ===========================================
# Filename Generation Settings
# ===========================================

# Maximum length of descriptive part (before UUID suffix)
FILENAME_MAX_LENGTH = 50

# Number of words to extract from text (Option A)
FILENAME_WORD_COUNT = 6

# Enable AI-powered title generation (Option B)
# Requires Azure OpenAI configuration (see implementation plan)
FILENAME_USE_AI = False

# Max tokens for AI-generated title (Option B only)
FILENAME_AI_MAX_TOKENS = 10

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
# Character Voice Expressions (NEW!)
# ==========================================

# Enable automatic character voice detection
# When True, parses dialogue and assigns different voices to characters
# Female characters get female voices, male get male voices
# Expressions like "whispered" or "shouted" apply appropriate styles
ENABLE_CHARACTER_VOICES = False  # Set to True to enable by default

# Custom character-to-voice mappings (optional)
# Override automatic detection for specific characters
CHARACTER_VOICE_OVERRIDES = {
    # Example:
    # "narrator": {"voice": "en-US-GuyNeural", "style": "friendly"},
    # "princess": {"voice": "en-US-JennyNeural", "style": "cheerful", "gender": "female"},
    # "dragon": {"voice": "en-US-DavisNeural", "style": "angry", "gender": "male"},
}

# Narrator settings (used for non-dialogue text)
NARRATOR_VOICE = "en-US-GuyNeural"
NARRATOR_STYLE = "friendly"

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
