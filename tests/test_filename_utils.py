"""
Unit tests for filename_utils.py
"""
import pytest
from filename_utils import (
    extract_first_words,
    sanitize_for_filename,
    generate_descriptive_filename,
    generate_filename_with_uuid,
    generate_synthesis_id
)


class TestExtractFirstWords:
    """Tests for extract_first_words function"""
    
    def test_basic_extraction(self):
        """Extract first N words from normal text"""
        text = "Once upon a time there was a brave dragon"
        result = extract_first_words(text, 6)
        assert result == "Once upon a time there was"
    
    def test_fewer_words_than_requested(self):
        """Handle text with fewer words than requested"""
        text = "Short text"
        result = extract_first_words(text, 6)
        assert result == "Short text"
    
    def test_empty_string(self):
        """Handle empty string"""
        result = extract_first_words("", 6)
        assert result == ""
    
    def test_none_input(self):
        """Handle None input"""
        result = extract_first_words(None, 6)
        assert result == ""
    
    def test_single_word(self):
        """Handle single word"""
        result = extract_first_words("Hello", 6)
        assert result == "Hello"
    
    def test_whitespace_variations(self):
        """Handle multiple whitespace characters"""
        text = "Once   upon    a   time"
        result = extract_first_words(text, 4)
        assert result == "Once upon a time"
    
    def test_custom_word_count(self):
        """Test different word counts"""
        text = "One two three four five six seven eight"
        assert extract_first_words(text, 3) == "One two three"
        assert extract_first_words(text, 1) == "One"
        assert extract_first_words(text, 10) == "One two three four five six seven eight"


class TestSanitizeForFilename:
    """Tests for sanitize_for_filename function"""
    
    def test_basic_sanitization(self):
        """Basic text sanitization"""
        result = sanitize_for_filename("The Brave Little Dragon!")
        assert result == "the-brave-little-dragon"
    
    def test_special_characters_removed(self):
        """Remove special characters"""
        result = sanitize_for_filename("Test@#$%^&*()")
        assert result == "test"
    
    def test_multiple_spaces(self):
        """Handle multiple spaces"""
        result = sanitize_for_filename("Hello   World")
        assert result == "hello-world"
    
    def test_max_length_truncation(self):
        """Truncate to max length"""
        long_text = "a" * 100
        result = sanitize_for_filename(long_text, max_length=50)
        assert len(result) <= 50
    
    def test_truncate_at_hyphen(self):
        """Prefer truncating at hyphen boundary"""
        text = "This is a very long text that should be truncated nicely"
        result = sanitize_for_filename(text, max_length=30)
        assert not result.endswith("-")
        assert len(result) <= 30
    
    def test_empty_string(self):
        """Handle empty string"""
        result = sanitize_for_filename("")
        assert result == ""
    
    def test_none_input(self):
        """Handle None input"""
        result = sanitize_for_filename(None)
        assert result == ""
    
    def test_numbers_preserved(self):
        """Numbers should be preserved"""
        result = sanitize_for_filename("Chapter 1 Section 2")
        assert result == "chapter-1-section-2"
    
    def test_leading_trailing_hyphens_removed(self):
        """Leading and trailing hyphens removed"""
        result = sanitize_for_filename("---Hello World---")
        assert result == "hello-world"


class TestGenerateDescriptiveFilename:
    """Tests for generate_descriptive_filename function"""
    
    def test_basic_generation(self):
        """Generate filename from normal text"""
        text = "Once upon a time, a brave dragon flew over the mountains"
        result = generate_descriptive_filename(text)
        assert result == "once-upon-a-time-a-brave"
    
    def test_fallback_on_empty(self):
        """Fallback to 'audio' if text produces empty result"""
        result = generate_descriptive_filename("@#$%")
        assert result == "audio"
    
    def test_ai_mode_raises(self):
        """AI mode should raise NotImplementedError"""
        with pytest.raises(NotImplementedError):
            generate_descriptive_filename("test", use_ai=True)
    
    def test_custom_parameters(self):
        """Test with custom max_length and word_count"""
        text = "The quick brown fox jumps over the lazy dog"
        result = generate_descriptive_filename(text, max_length=20, word_count=3)
        assert len(result) <= 20


class TestGenerateFilenameWithUuid:
    """Tests for generate_filename_with_uuid function"""
    
    def test_format(self):
        """Check filename format with UUID suffix"""
        text = "Once upon a time"
        result = generate_filename_with_uuid(text)
        
        # Should match pattern: descriptive_uuid.mp3
        parts = result.rsplit("_", 1)
        assert len(parts) == 2
        assert parts[1].endswith(".mp3")
        
        # UUID part should be 8 chars + .mp3
        uuid_part = parts[1].replace(".mp3", "")
        assert len(uuid_part) == 8
    
    def test_custom_extension(self):
        """Test with custom extension"""
        result = generate_filename_with_uuid("Test", extension=".wav")
        assert result.endswith(".wav")
    
    def test_uniqueness(self):
        """Each call should produce unique filename"""
        text = "Same text"
        result1 = generate_filename_with_uuid(text)
        result2 = generate_filename_with_uuid(text)
        assert result1 != result2


class TestGenerateSynthesisId:
    """Tests for generate_synthesis_id function"""
    
    def test_format(self):
        """Check synthesis ID format"""
        text = "Once upon a time"
        result = generate_synthesis_id(text)
        
        # Should match pattern: descriptive_uuid (no extension)
        parts = result.rsplit("_", 1)
        assert len(parts) == 2
        assert len(parts[1]) == 8  # Short UUID
    
    def test_no_extension(self):
        """Synthesis ID should not have file extension"""
        result = generate_synthesis_id("Test text")
        assert not result.endswith(".mp3")
        assert not result.endswith(".wav")
    
    def test_uniqueness(self):
        """Each call should produce unique ID"""
        text = "Same text"
        result1 = generate_synthesis_id(text)
        result2 = generate_synthesis_id(text)
        assert result1 != result2
