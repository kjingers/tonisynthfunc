"""
Input Validators Module

Centralized input validation for API requests.
"""
import re
from typing import Optional, List, Tuple
from story_config import (
    VOICE_STYLES,
    STORY_PRESETS,
    MAX_TEXT_LENGTH,
    MIN_TEXT_LENGTH,
    MAX_BATCH_TEXT_LENGTH,
)


class ValidationResult:
    """Result of a validation check"""
    
    def __init__(
        self,
        is_valid: bool,
        error: Optional[str] = None,
        field: Optional[str] = None
    ):
        self.is_valid = is_valid
        self.error = error
        self.field = field
    
    @staticmethod
    def valid() -> "ValidationResult":
        return ValidationResult(True)
    
    @staticmethod
    def invalid(error: str, field: Optional[str] = None) -> "ValidationResult":
        return ValidationResult(False, error, field)


def validate_text(
    text: Optional[str],
    max_length: int = MAX_TEXT_LENGTH,
    min_length: int = MIN_TEXT_LENGTH,
    field_name: str = "text"
) -> ValidationResult:
    """
    Validate text input.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        min_length: Minimum required length
        field_name: Name of field for error messages
        
    Returns:
        ValidationResult
    """
    if text is None:
        return ValidationResult.invalid(f"{field_name} is required", field_name)
    
    text = text.strip()
    
    if len(text) < min_length:
        return ValidationResult.invalid(
            f"{field_name} must be at least {min_length} characters",
            field_name
        )
    
    if len(text) > max_length:
        return ValidationResult.invalid(
            f"{field_name} must not exceed {max_length} characters",
            field_name
        )
    
    return ValidationResult.valid()


def validate_voice(voice: Optional[str]) -> ValidationResult:
    """
    Validate voice selection.
    
    Args:
        voice: Voice name to validate
        
    Returns:
        ValidationResult
    """
    if not voice:
        return ValidationResult.valid()  # Optional field
    
    # Voice format: en-US-AriaNeural, etc.
    pattern = r'^[a-z]{2,3}-[A-Z]{2}-\w+Neural$'
    
    if not re.match(pattern, voice):
        return ValidationResult.invalid(
            f"Invalid voice format: {voice}. Expected format: 'en-US-VoiceNameNeural'",
            "voice"
        )
    
    return ValidationResult.valid()


def validate_style(style: Optional[str], voice: Optional[str] = None) -> ValidationResult:
    """
    Validate speaking style.
    
    Args:
        style: Style name to validate
        voice: Voice name for style compatibility check
        
    Returns:
        ValidationResult
    """
    if not style:
        return ValidationResult.valid()  # Optional field
    
    all_styles = set()
    for styles in VOICE_STYLES.values():
        all_styles.update(styles)
    
    if style not in all_styles:
        return ValidationResult.invalid(
            f"Invalid style: {style}. Available styles: {', '.join(sorted(all_styles))}",
            "style"
        )
    
    # Check if style is compatible with voice
    if voice:
        voice_styles = VOICE_STYLES.get(voice, [])
        if style not in voice_styles:
            # This is a warning, not an error - style may still work
            pass
    
    return ValidationResult.valid()


def validate_preset(preset: Optional[str]) -> ValidationResult:
    """
    Validate story preset.
    
    Args:
        preset: Preset name to validate
        
    Returns:
        ValidationResult
    """
    if not preset:
        return ValidationResult.valid()  # Optional field
    
    if preset not in STORY_PRESETS:
        available = ', '.join(sorted(STORY_PRESETS.keys()))
        return ValidationResult.invalid(
            f"Invalid preset: {preset}. Available presets: {available}",
            "preset"
        )
    
    return ValidationResult.valid()


def validate_filename_title(title: Optional[str]) -> ValidationResult:
    """
    Validate title for filename generation.
    
    Args:
        title: Title to validate
        
    Returns:
        ValidationResult
    """
    if not title:
        return ValidationResult.valid()  # Will use default
    
    # Remove potentially problematic characters for validation
    # Actual sanitization happens in filename_utils
    if len(title) > 200:
        return ValidationResult.invalid(
            "Title must not exceed 200 characters",
            "filename_title"
        )
    
    return ValidationResult.valid()


def validate_batch_start_request(
    text: Optional[str],
    voice: Optional[str] = None,
    style: Optional[str] = None,
    preset: Optional[str] = None,
    title: Optional[str] = None
) -> ValidationResult:
    """
    Validate all inputs for batch start request.
    
    Args:
        text: Text to synthesize
        voice: Voice selection
        style: Speaking style
        preset: Story preset
        title: Filename title
        
    Returns:
        First validation error found, or valid result
    """
    validators = [
        lambda: validate_text(text, max_length=MAX_BATCH_TEXT_LENGTH),
        lambda: validate_voice(voice),
        lambda: validate_style(style, voice),
        lambda: validate_preset(preset),
        lambda: validate_filename_title(title),
    ]
    
    for validator in validators:
        result = validator()
        if not result.is_valid:
            return result
    
    return ValidationResult.valid()


def validate_synthesis_id(synthesis_id: Optional[str]) -> ValidationResult:
    """
    Validate synthesis job ID.
    
    Args:
        synthesis_id: ID to validate
        
    Returns:
        ValidationResult
    """
    if not synthesis_id:
        return ValidationResult.invalid(
            "synthesis_id is required",
            "synthesis_id"
        )
    
    # UUID format or Azure's synthesis ID format
    if len(synthesis_id) < 10 or len(synthesis_id) > 100:
        return ValidationResult.invalid(
            "Invalid synthesis_id format",
            "synthesis_id"
        )
    
    # Check for invalid characters
    if not re.match(r'^[\w\-]+$', synthesis_id):
        return ValidationResult.invalid(
            "synthesis_id contains invalid characters",
            "synthesis_id"
        )
    
    return ValidationResult.valid()


def is_adventure_mode_text(text: str) -> bool:
    """
    Detect if text should automatically enable adventure/story mode.
    
    Adventure mode enables multi-voice character expressions when the text
    appears to be a story or adventure narrative.
    
    Args:
        text: The input text to analyze
        
    Returns:
        True if text appears to be a story/adventure
    """
    if not text:
        return False
    
    # Get first N words
    words = text.lower().split()[:10]
    
    # Check for story/adventure keywords in the beginning
    story_keywords = {'story', 'adventure', 'tale', 'once', 'upon'}
    
    for word in words:
        # Clean punctuation
        clean_word = re.sub(r'[^\w]', '', word)
        if clean_word in story_keywords:
            return True
    
    # Check for common story opening patterns
    text_lower = text.lower()[:100]  # Check first 100 chars
    story_patterns = [
        r'^once upon a time',
        r'^in a land far',
        r'^long ago',
        r'^the story of',
        r'^a tale of',
        r"^chapter \d",
        r'^prologue',
    ]
    
    for pattern in story_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False
