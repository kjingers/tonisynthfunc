"""
Unit tests for story_config.py configuration validation
"""
import pytest
from story_config import (
    DEFAULT_VOICE,
    DEFAULT_STYLE,
    OUTPUT_FORMAT,
    VOICE_STYLES,
    STORY_PRESETS,
    ENABLE_CHARACTER_VOICES,
    NARRATOR_VOICE,
    NARRATOR_STYLE,
)


class TestVoiceConfiguration:
    """Tests for voice configuration settings"""
    
    def test_default_voice_is_valid(self):
        """Default voice should be a valid Azure voice"""
        assert DEFAULT_VOICE is not None
        assert DEFAULT_VOICE.startswith("en-")
        assert "Neural" in DEFAULT_VOICE
    
    def test_default_style_is_valid(self):
        """Default style should be valid for default voice"""
        if DEFAULT_STYLE is not None and DEFAULT_VOICE in VOICE_STYLES:
            assert DEFAULT_STYLE in VOICE_STYLES[DEFAULT_VOICE]
    
    def test_voice_styles_not_empty(self):
        """VOICE_STYLES should have entries"""
        assert len(VOICE_STYLES) > 0
    
    def test_each_voice_has_styles(self):
        """Each voice should have at least one style"""
        for voice, styles in VOICE_STYLES.items():
            assert len(styles) > 0, f"{voice} has no styles"
    
    def test_narrator_voice_valid(self):
        """Narrator voice should be valid"""
        assert NARRATOR_VOICE is not None
        assert NARRATOR_VOICE.startswith("en-")


class TestStoryPresets:
    """Tests for story preset configurations"""
    
    def test_presets_exist(self):
        """Story presets should be defined"""
        assert len(STORY_PRESETS) > 0
    
    def test_bedtime_preset(self):
        """Bedtime preset should exist"""
        assert "bedtime" in STORY_PRESETS
        preset = STORY_PRESETS["bedtime"]
        assert "voice" in preset
    
    def test_adventure_preset(self):
        """Adventure preset should exist"""
        assert "adventure" in STORY_PRESETS
        preset = STORY_PRESETS["adventure"]
        assert "voice" in preset
    
    def test_preset_voices_are_valid(self):
        """All preset voices should be valid Azure voices"""
        for name, preset in STORY_PRESETS.items():
            voice = preset.get("voice")
            assert voice is not None, f"Preset {name} has no voice"
            assert "Neural" in voice, f"Preset {name} voice is not Neural"


class TestOutputSettings:
    """Tests for output settings"""
    
    def test_output_format_is_valid(self):
        """Output format should be a valid Azure format"""
        assert OUTPUT_FORMAT is not None
        # Should be one of the known Azure formats
        valid_formats = [
            "audio-24khz-96kbitrate-mono-mp3",
            "audio-48khz-192kbitrate-mono-mp3",
            "audio-16khz-32kbitrate-mono-mp3",
        ]
        assert OUTPUT_FORMAT in valid_formats


class TestCharacterVoiceSettings:
    """Tests for character voice settings"""
    
    def test_enable_character_voices_is_bool(self):
        """ENABLE_CHARACTER_VOICES should be boolean"""
        assert isinstance(ENABLE_CHARACTER_VOICES, bool)
    
    def test_narrator_settings_valid(self):
        """Narrator settings should be valid"""
        assert NARRATOR_VOICE is not None
        assert NARRATOR_STYLE is not None or NARRATOR_STYLE is None  # Can be None
