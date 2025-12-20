"""
Tests for gender_detection module.

Tests the LLM-assisted gender detection functionality with mocked OpenAI calls.
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from gender_detection import (
    CharacterInfo,
    GenderDetectionError,
    get_cache_key,
    extract_all_character_names,
    analyze_characters_with_llm,
    detect_gender_with_llm,
    clear_cache,
    is_llm_available,
)


class TestCharacterInfo:
    """Tests for CharacterInfo dataclass"""
    
    def test_create_character_info(self):
        """Test creating a CharacterInfo object"""
        info = CharacterInfo(
            name="Elena",
            gender="female",
            aliases=["princess", "the princess"],
            reasoning="Name Elena is typically female"
        )
        assert info.name == "Elena"
        assert info.gender == "female"
        assert "princess" in info.aliases
        assert "typically female" in info.reasoning


class TestCacheKey:
    """Tests for cache key generation"""
    
    def test_cache_key_consistent(self):
        """Same text produces same cache key"""
        text = "Once upon a time, there was a brave knight."
        key1 = get_cache_key(text)
        key2 = get_cache_key(text)
        assert key1 == key2
    
    def test_cache_key_different_for_different_text(self):
        """Different text produces different cache key"""
        text1 = "Once upon a time, there was a brave knight."
        text2 = "The princess lived in a tall tower."
        key1 = get_cache_key(text1)
        key2 = get_cache_key(text2)
        assert key1 != key2
    
    def test_cache_key_uses_first_1000_chars(self):
        """Cache key only considers first 1000 characters"""
        base_text = "A" * 1000
        text1 = base_text + "DIFFERENT_ENDING_1"
        text2 = base_text + "DIFFERENT_ENDING_2"
        key1 = get_cache_key(text1)
        key2 = get_cache_key(text2)
        # Keys should be same since first 1000 chars are identical
        assert key1 == key2


class TestExtractCharacterNames:
    """Tests for character name extraction"""
    
    def test_extract_titled_names(self):
        """Extract names with titles"""
        text = "Sir Cedric rode into battle. Princess Elena watched from the tower."
        names = extract_all_character_names(text)
        assert "Sir Cedric" in names
        assert "Princess Elena" in names
    
    def test_extract_names_before_speech_verbs(self):
        """Extract names that appear before speech verbs"""
        text = 'Mary said "Hello!" Tom replied quietly.'
        names = extract_all_character_names(text)
        assert "Mary" in names
        assert "Tom" in names
    
    def test_extract_names_after_speech_verbs(self):
        """Extract names that appear after speech verbs"""
        text = '"Hello!" said James. "Welcome," whispered Sarah.'
        names = extract_all_character_names(text)
        assert "James" in names
        assert "Sarah" in names
    
    def test_extract_role_references(self):
        """Extract 'the [role]' patterns"""
        text = "The dragon breathed fire. The knight raised his shield. The wizard cast a spell."
        names = extract_all_character_names(text)
        assert "the dragon" in names
        assert "the knight" in names
        assert "the wizard" in names
    
    def test_filter_common_words(self):
        """Common words should be filtered out"""
        text = '"Hello!" said The boy. And all was well.'
        names = extract_all_character_names(text)
        # 'The', 'And', 'all' should not be in names
        assert "the" not in [n.lower() for n in names]
        assert "and" not in [n.lower() for n in names]
        assert "all" not in [n.lower() for n in names]


class TestAnalyzeCharactersWithLLM:
    """Tests for LLM-based character analysis"""
    
    @patch('gender_detection.get_openai_client')
    def test_returns_empty_when_no_client(self, mock_get_client):
        """Returns empty dict when OpenAI client unavailable"""
        mock_get_client.return_value = None
        
        result = analyze_characters_with_llm("Some text", ["Elena", "Cedric"])
        assert result == {}
    
    @patch('gender_detection.get_openai_client')
    @patch('gender_detection.os.environ.get')
    def test_analyze_characters_success(self, mock_env, mock_get_client):
        """Successfully analyze characters with mocked LLM"""
        mock_env.return_value = "gpt-4o-mini"
        
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "characters": {
                "Elena": {
                    "gender": "female",
                    "aliases": ["princess", "the princess"],
                    "reasoning": "Elena is a traditionally female name"
                },
                "Cedric": {
                    "gender": "male",
                    "aliases": ["sir cedric", "the knight"],
                    "reasoning": "Cedric is a traditionally male name"
                }
            }
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        text = "Princess Elena met Sir Cedric at the castle."
        result = analyze_characters_with_llm(text, ["Elena", "Cedric"])
        
        assert "elena" in result
        assert "cedric" in result
        assert result["elena"].gender == "female"
        assert result["cedric"].gender == "male"
        assert "princess" in result["elena"].aliases
    
    @patch('gender_detection.get_openai_client')
    def test_handle_invalid_json_response(self, mock_get_client):
        """Handle invalid JSON response gracefully"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        result = analyze_characters_with_llm("Some text", ["Elena"])
        assert result == {}


class TestDetectGenderWithLLM:
    """Tests for the main gender detection function"""
    
    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()
    
    @patch('gender_detection.analyze_characters_with_llm')
    def test_detect_gender_uses_cache(self, mock_analyze):
        """Second call should use cache"""
        mock_analyze.return_value = {
            "elena": CharacterInfo(
                name="Elena",
                gender="female",
                aliases=[],
                reasoning="Female name"
            )
        }
        
        text = "Princess Elena lived in a castle."
        
        # First call
        gender1, _ = detect_gender_with_llm("Elena", text)
        assert gender1 == "female"
        
        # Second call should use cache (analyze not called again)
        mock_analyze.reset_mock()
        gender2, _ = detect_gender_with_llm("Elena", text)
        assert gender2 == "female"
        mock_analyze.assert_not_called()
    
    @patch('gender_detection.analyze_characters_with_llm')
    def test_detect_gender_by_alias(self, mock_analyze):
        """Should find character by alias"""
        mock_analyze.return_value = {
            "sir cedric": CharacterInfo(
                name="Sir Cedric",
                gender="male",
                aliases=["the knight", "cedric"],
                reasoning="Male title and name"
            )
        }
        
        text = "Sir Cedric, the brave knight, rode forth."
        
        # First call to populate cache
        detect_gender_with_llm("Sir Cedric", text)
        
        # Look up by alias
        gender, reasoning = detect_gender_with_llm("the knight", text)
        assert gender == "male"
        assert "Alias of" in reasoning
    
    @patch('gender_detection.analyze_characters_with_llm')
    def test_neutral_when_not_found(self, mock_analyze):
        """Returns neutral when character not found"""
        mock_analyze.return_value = {}
        
        gender, reasoning = detect_gender_with_llm("UnknownCharacter", "Some text")
        assert gender == "neutral"
        assert "Could not determine" in reasoning


class TestIsLLMAvailable:
    """Tests for LLM availability check"""
    
    @patch('gender_detection.OPENAI_AVAILABLE', True)
    @patch('gender_detection.os.environ.get')
    def test_available_when_configured(self, mock_env):
        """Returns True when OpenAI is configured"""
        def env_side_effect(key):
            if key == "AZURE_OPENAI_ENDPOINT":
                return "https://my-endpoint.openai.azure.com"
            if key == "AZURE_OPENAI_API_KEY":
                return "my-api-key"
            return None
        
        mock_env.side_effect = env_side_effect
        assert is_llm_available() == True
    
    @patch('gender_detection.OPENAI_AVAILABLE', True)
    @patch('gender_detection.os.environ.get')
    def test_unavailable_when_not_configured(self, mock_env):
        """Returns False when OpenAI is not configured"""
        mock_env.return_value = None
        assert is_llm_available() == False
    
    @patch('gender_detection.OPENAI_AVAILABLE', False)
    def test_unavailable_when_sdk_missing(self):
        """Returns False when OpenAI SDK not installed"""
        assert is_llm_available() == False


class TestClearCache:
    """Tests for cache clearing"""
    
    @patch('gender_detection.analyze_characters_with_llm')
    def test_clear_cache_removes_entries(self, mock_analyze):
        """Clearing cache should force new analysis"""
        mock_analyze.return_value = {
            "elena": CharacterInfo(
                name="Elena",
                gender="female",
                aliases=[],
                reasoning="Female name"
            )
        }
        
        text = "Princess Elena lived in a castle."
        
        # First call
        detect_gender_with_llm("Elena", text)
        assert mock_analyze.call_count == 1
        
        # Clear cache
        clear_cache()
        
        # Should call analyze again
        detect_gender_with_llm("Elena", text)
        assert mock_analyze.call_count == 2
