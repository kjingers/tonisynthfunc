"""
Unit tests for validators.py

Tests input validation functions and adventure mode detection.
"""
import pytest
from validators import (
    ValidationResult,
    validate_text,
    validate_voice,
    validate_style,
    validate_preset,
    validate_filename_title,
    validate_batch_start_request,
    validate_synthesis_id,
    is_adventure_mode_text
)


class TestValidationResult:
    """Tests for ValidationResult class"""
    
    def test_valid_result(self):
        result = ValidationResult.valid()
        assert result.is_valid is True
        assert result.error is None
        assert result.field is None
    
    def test_invalid_result(self):
        result = ValidationResult.invalid("test error", "test_field")
        assert result.is_valid is False
        assert result.error == "test error"
        assert result.field == "test_field"


class TestValidateText:
    """Tests for validate_text function"""
    
    def test_valid_text(self):
        result = validate_text("This is valid text for synthesis")
        assert result.is_valid
    
    def test_none_text_returns_error(self):
        result = validate_text(None)
        assert not result.is_valid
        assert "required" in result.error.lower()
    
    def test_empty_text_returns_error(self):
        result = validate_text("")
        assert not result.is_valid
    
    def test_whitespace_only_returns_error(self):
        result = validate_text("   ")
        assert not result.is_valid
    
    def test_text_too_long(self):
        long_text = "a" * 1000001
        result = validate_text(long_text, max_length=1000000)
        assert not result.is_valid
        assert "exceed" in result.error.lower()
    
    def test_custom_field_name_in_error(self):
        result = validate_text(None, field_name="my_field")
        assert "my_field" in result.error


class TestValidateVoice:
    """Tests for validate_voice function"""
    
    def test_valid_voice_format(self):
        result = validate_voice("en-US-GuyNeural")
        assert result.is_valid
    
    def test_empty_voice_is_valid(self):
        """Empty voice should be valid (optional)"""
        result = validate_voice(None)
        assert result.is_valid
        
        result = validate_voice("")
        assert result.is_valid
    
    def test_invalid_voice_format(self):
        result = validate_voice("invalid-voice")
        assert not result.is_valid
        assert "format" in result.error.lower()
    
    def test_various_valid_voices(self):
        valid_voices = [
            "en-US-AriaNeural",
            "en-GB-RyanNeural",
            "de-DE-KatjaNeural",
            "zh-CN-XiaoxiaoNeural"
        ]
        for voice in valid_voices:
            result = validate_voice(voice)
            assert result.is_valid, f"Voice {voice} should be valid"


class TestValidateStyle:
    """Tests for validate_style function"""
    
    def test_empty_style_is_valid(self):
        """Empty style should be valid (optional)"""
        result = validate_style(None)
        assert result.is_valid
    
    def test_valid_style(self):
        result = validate_style("friendly")
        assert result.is_valid
    
    def test_invalid_style(self):
        result = validate_style("nonexistent_style_xyz")
        assert not result.is_valid


class TestValidatePreset:
    """Tests for validate_preset function"""
    
    def test_empty_preset_is_valid(self):
        result = validate_preset(None)
        assert result.is_valid
    
    def test_valid_preset(self):
        result = validate_preset("bedtime")
        assert result.is_valid
    
    def test_invalid_preset(self):
        result = validate_preset("invalid_preset")
        assert not result.is_valid


class TestValidateFilenameTitle:
    """Tests for validate_filename_title function"""
    
    def test_empty_title_is_valid(self):
        result = validate_filename_title(None)
        assert result.is_valid
    
    def test_valid_title(self):
        result = validate_filename_title("My Awesome Story")
        assert result.is_valid
    
    def test_title_too_long(self):
        long_title = "a" * 250
        result = validate_filename_title(long_title)
        assert not result.is_valid


class TestValidateBatchStartRequest:
    """Tests for complete batch start request validation"""
    
    def test_valid_request(self):
        result = validate_batch_start_request(
            text="This is a valid story text.",
            voice="en-US-GuyNeural",
            style="friendly"
        )
        assert result.is_valid
    
    def test_missing_text_fails(self):
        result = validate_batch_start_request(
            text=None,
            voice="en-US-GuyNeural"
        )
        assert not result.is_valid
        assert result.field == "text"


class TestValidateSynthesisId:
    """Tests for validate_synthesis_id function"""
    
    def test_valid_synthesis_id(self):
        result = validate_synthesis_id("my-story-dragon-adventure-12345678")
        assert result.is_valid
    
    def test_empty_synthesis_id(self):
        result = validate_synthesis_id(None)
        assert not result.is_valid
    
    def test_short_synthesis_id(self):
        result = validate_synthesis_id("short")
        assert not result.is_valid
    
    def test_invalid_characters(self):
        result = validate_synthesis_id("id with spaces")
        assert not result.is_valid


class TestIsAdventureModeText:
    """Tests for is_adventure_mode_text function - story/adventure auto-detection"""
    
    def test_story_keyword_detected(self):
        """Text starting with 'story' should be detected"""
        assert is_adventure_mode_text("A Story About Dragons")
        assert is_adventure_mode_text("The story begins here")
        assert is_adventure_mode_text("STORY TIME: Once upon a time")
    
    def test_adventure_keyword_detected(self):
        """Text with 'adventure' should be detected"""
        assert is_adventure_mode_text("The Great Adventure")
        assert is_adventure_mode_text("Adventure time begins")
    
    def test_tale_keyword_detected(self):
        """Text with 'tale' should be detected"""
        assert is_adventure_mode_text("A Tale of Two Cities")
        assert is_adventure_mode_text("The tale begins")
    
    def test_once_upon_a_time_pattern(self):
        """Classic story opening should be detected"""
        assert is_adventure_mode_text("Once upon a time, there was a princess")
        assert is_adventure_mode_text("ONCE UPON A TIME in a land far away")
    
    def test_in_a_land_far_pattern(self):
        """'In a land far' pattern should be detected"""
        assert is_adventure_mode_text("In a land far, far away")
    
    def test_long_ago_pattern(self):
        """'Long ago' pattern should be detected"""
        assert is_adventure_mode_text("Long ago, in ancient times")
    
    def test_chapter_pattern(self):
        """'Chapter 1' pattern should be detected"""
        assert is_adventure_mode_text("Chapter 1: The Beginning")
        assert is_adventure_mode_text("CHAPTER 2 - The Journey")
    
    def test_prologue_pattern(self):
        """'Prologue' should be detected"""
        assert is_adventure_mode_text("Prologue: Before the storm")
    
    def test_non_story_text_not_detected(self):
        """Regular text should not be detected as story"""
        assert not is_adventure_mode_text("Today we will learn about math")
        assert not is_adventure_mode_text("The weather is nice today")
        assert not is_adventure_mode_text("Please remember to buy milk")
        assert not is_adventure_mode_text("Meeting notes from Monday")
    
    def test_empty_text_returns_false(self):
        """Empty text should return False"""
        assert not is_adventure_mode_text("")
        assert not is_adventure_mode_text(None)
    
    def test_keyword_after_ten_words_not_detected(self):
        """Keywords after first 10 words should not trigger detection"""
        # Word count: 1-This 2-is 3-just 4-some 5-regular 6-text 7-with 8-nothing 9-special 10-in 11-it 12-story
        text = "This is just some regular text with nothing special in it story keyword"
        assert not is_adventure_mode_text(text)
    
    def test_keyword_with_punctuation(self):
        """Keywords with punctuation should still be detected"""
        assert is_adventure_mode_text("Story! A dragon appears")
        assert is_adventure_mode_text("'Adventure' begins now")
