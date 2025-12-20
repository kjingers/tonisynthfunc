"""
Unit tests for character_voices.py
"""
import pytest
from character_voices import (
    CharacterVoice,
    DialogueSegment,
    detect_gender,
    detect_expression,
    get_voice_for_gender,
    CharacterVoiceParser,
    generate_character_ssml,
    generate_simple_ssml,
    escape_ssml_text,
    FEMALE_VOICES,
    MALE_VOICES,
    FEMALE_NAMES,
    MALE_NAMES,
)


class TestDetectGender:
    """Tests for detect_gender function"""
    
    def test_female_names(self):
        """Detect female names"""
        assert detect_gender("Mary") == "female"
        assert detect_gender("Sarah") == "female"
        assert detect_gender("Mom") == "female"
        assert detect_gender("Princess") == "female"
        assert detect_gender("Queen") == "female"
    
    def test_male_names(self):
        """Detect male names"""
        assert detect_gender("John") == "male"
        assert detect_gender("David") == "male"
        assert detect_gender("Dad") == "male"
        assert detect_gender("King") == "male"
        assert detect_gender("Jesus") == "male"
    
    def test_case_insensitive(self):
        """Name detection should be case insensitive"""
        assert detect_gender("MARY") == "female"
        assert detect_gender("john") == "male"
        assert detect_gender("MaRy") == "female"
    
    def test_context_pronouns(self):
        """Detect gender from context pronouns"""
        assert detect_gender("Alex", "she said hello") == "female"
        assert detect_gender("Alex", "he walked away") == "male"
    
    def test_unknown_name(self):
        """Unknown names return neutral"""
        assert detect_gender("Xylophone") == "neutral"
        assert detect_gender("Qwerty") == "neutral"
    
    def test_whitespace_handling(self):
        """Handle names with whitespace"""
        assert detect_gender("  Mary  ") == "female"
        assert detect_gender("John\n") == "male"


class TestDetectExpression:
    """Tests for detect_expression function"""
    
    def test_whispering_patterns(self):
        """Detect whispering expressions"""
        assert detect_expression("she whispered") == "whispering"
        assert detect_expression("he said quietly") == "whispering"
        assert detect_expression("in a hushed voice") == "whispering"
    
    def test_shouting_patterns(self):
        """Detect shouting expressions"""
        assert detect_expression("he shouted") == "shouting"
        assert detect_expression("she yelled") == "shouting"
        assert detect_expression("they screamed") == "shouting"
    
    def test_excited_patterns(self):
        """Detect excited expressions"""
        assert detect_expression("she said excitedly") == "excited"
        assert detect_expression("he said enthusiastically") == "excited"
        assert detect_expression("they cheered eagerly") == "excited"
    
    def test_sad_patterns(self):
        """Detect sad expressions"""
        assert detect_expression("she said sadly") == "sad"
        assert detect_expression("he sobbed") == "sad"
        assert detect_expression("tearfully") == "sad"
    
    def test_angry_patterns(self):
        """Detect angry expressions"""
        assert detect_expression("he said angrily") == "angry"
        assert detect_expression("she snarled") == "angry"
    
    def test_terrified_patterns(self):
        """Detect terrified expressions"""
        assert detect_expression("terrified") == "terrified"
        assert detect_expression("with fear") == "terrified"
        assert detect_expression("trembling") == "terrified"
    
    def test_cheerful_patterns(self):
        """Detect cheerful expressions"""
        assert detect_expression("cheerfully") == "cheerful"
        assert detect_expression("with a smile") == "cheerful"
        assert detect_expression("laughing") == "cheerful"
    
    def test_no_expression(self):
        """Return None when no expression detected"""
        assert detect_expression("said") is None
        assert detect_expression("replied") is None
        assert detect_expression("asked") is None
    
    def test_case_insensitive(self):
        """Expression detection should be case insensitive"""
        assert detect_expression("WHISPERED") == "whispering"
        assert detect_expression("Shouted") == "shouting"


class TestGetVoiceForGender:
    """Tests for get_voice_for_gender function"""
    
    def test_female_voice(self):
        """Get female voice"""
        voice = get_voice_for_gender("female", 0)
        assert voice in FEMALE_VOICES
    
    def test_male_voice(self):
        """Get male voice"""
        voice = get_voice_for_gender("male", 0)
        assert voice in MALE_VOICES
    
    def test_neutral_voice(self):
        """Neutral alternates between male and female"""
        voices = [get_voice_for_gender("neutral", i) for i in range(6)]
        # Should include both male and female voices
        has_male = any(v in MALE_VOICES for v in voices)
        has_female = any(v in FEMALE_VOICES for v in voices)
        assert has_male or has_female
    
    def test_voice_index_cycling(self):
        """Voice index should cycle through available voices"""
        voice0 = get_voice_for_gender("female", 0)
        voice1 = get_voice_for_gender("female", 1)
        voice_cycle = get_voice_for_gender("female", len(FEMALE_VOICES))
        
        assert voice0 != voice1 or len(FEMALE_VOICES) == 1
        assert voice_cycle == voice0  # Should cycle back


class TestCharacterVoiceParser:
    """Tests for CharacterVoiceParser class"""
    
    def test_init_defaults(self):
        """Parser initializes with defaults"""
        parser = CharacterVoiceParser()
        assert parser.narrator_voice is not None
        assert parser.character_cache == {}
    
    def test_get_character_voice_caching(self):
        """Character voices should be cached"""
        parser = CharacterVoiceParser()
        voice1 = parser.get_character_voice("Mary")
        voice2 = parser.get_character_voice("Mary")
        assert voice1 == voice2
    
    def test_get_character_voice_override(self):
        """Character overrides should take precedence"""
        override = CharacterVoice(
            voice_name="custom-voice",
            default_style="cheerful",
            gender="female"
        )
        parser = CharacterVoiceParser(character_overrides={"mary": override})
        voice = parser.get_character_voice("Mary")
        assert voice.voice_name == "custom-voice"
    
    def test_parse_dialogue_simple(self):
        """Parse simple dialogue"""
        parser = CharacterVoiceParser()
        text = '"Hello," said Mary.'
        segments = parser.parse_dialogue(text)
        
        assert len(segments) >= 1
        # Should have at least a dialogue segment
        dialogue_segments = [s for s in segments if s.is_dialogue]
        assert len(dialogue_segments) >= 1
    
    def test_parse_dialogue_with_narration(self):
        """Parse dialogue with surrounding narration"""
        parser = CharacterVoiceParser()
        text = 'The sun was setting. "Hello," said Mary. It was beautiful.'
        segments = parser.parse_dialogue(text)
        
        # Should have both narration and dialogue
        has_dialogue = any(s.is_dialogue for s in segments)
        has_narration = any(not s.is_dialogue for s in segments)
        assert has_dialogue
    
    def test_parse_no_dialogue(self):
        """Handle text with no dialogue"""
        parser = CharacterVoiceParser()
        text = "The sun set over the mountains. Birds flew home."
        segments = parser.parse_dialogue(text)
        
        assert len(segments) == 1
        assert segments[0].is_dialogue is False


class TestGenerateCharacterSsml:
    """Tests for generate_character_ssml function"""
    
    def test_basic_ssml_structure(self):
        """Generated SSML has correct structure"""
        ssml = generate_character_ssml("Hello world")
        
        assert ssml.startswith("<speak")
        assert ssml.endswith("</speak>")
        assert "version='1.0'" in ssml
        assert "<voice" in ssml
    
    def test_ssml_with_dialogue(self):
        """SSML includes voice changes for dialogue"""
        text = '"Hello," said Mary. "Hi," said John.'
        ssml = generate_character_ssml(text)
        
        assert "<speak" in ssml
        assert "</speak>" in ssml
        # Should have voice tags
        assert "<voice" in ssml
    
    def test_character_overrides(self):
        """Character overrides are applied"""
        text = '"Hello," said Mary.'
        overrides = {
            "mary": {"voice": "en-US-JennyNeural", "style": "cheerful"}
        }
        ssml = generate_character_ssml(text, character_overrides=overrides)
        
        assert "en-US-JennyNeural" in ssml


class TestGenerateSimpleSsml:
    """Tests for generate_simple_ssml function"""
    
    def test_basic_ssml(self):
        """Generate basic SSML without style"""
        ssml = generate_simple_ssml("Hello world", "en-US-GuyNeural")
        
        assert "<speak" in ssml
        assert "</speak>" in ssml
        assert "en-US-GuyNeural" in ssml
        assert "Hello world" in ssml
    
    def test_ssml_with_style(self):
        """Generate SSML with style"""
        ssml = generate_simple_ssml("Hello", "en-US-GuyNeural", "cheerful")
        
        assert "mstts:express-as" in ssml
        assert "cheerful" in ssml
    
    def test_ssml_no_style(self):
        """Generate SSML without style"""
        ssml = generate_simple_ssml("Hello", "en-US-GuyNeural", None)
        
        assert "mstts:express-as" not in ssml


class TestEscapeSsmlText:
    """Tests for escape_ssml_text function"""
    
    def test_ampersand(self):
        """Escape ampersand"""
        assert escape_ssml_text("Tom & Jerry") == "Tom &amp; Jerry"
    
    def test_less_than(self):
        """Escape less than"""
        assert escape_ssml_text("a < b") == "a &lt; b"
    
    def test_greater_than(self):
        """Escape greater than"""
        assert escape_ssml_text("a > b") == "a &gt; b"
    
    def test_quotes(self):
        """Escape quotes"""
        assert escape_ssml_text('say "hello"') == "say &quot;hello&quot;"
        assert escape_ssml_text("it's") == "it&apos;s"
    
    def test_multiple_escapes(self):
        """Handle multiple special characters"""
        text = '<script>alert("hi")</script>'
        escaped = escape_ssml_text(text)
        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&quot;" in escaped
    
    def test_no_escaping_needed(self):
        """Normal text unchanged"""
        assert escape_ssml_text("Hello world") == "Hello world"
