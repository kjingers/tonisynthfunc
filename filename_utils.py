"""
Filename utilities for generating descriptive audio filenames.

This module provides functions to generate descriptive filenames based on
input text content, replacing generic UUID-only names with meaningful names.

Example:
    Input text: "Once upon a time, a brave little dragon..."
    Output: "once-upon-a-time-a-brave"
"""

import re
import uuid


def extract_first_words(text: str, word_count: int = 6) -> str:
    """
    Extract the first N words from text.
    
    Args:
        text: The input text to extract words from
        word_count: Maximum number of words to extract (default: 6)
    
    Returns:
        String containing the first N words joined by spaces
    
    Examples:
        >>> extract_first_words("Once upon a time there was a dragon", 6)
        'Once upon a time there was'
        >>> extract_first_words("Short", 6)
        'Short'
        >>> extract_first_words("", 6)
        ''
    """
    if not text:
        return ""
    
    # Split on whitespace and filter empty strings
    words = text.split()
    
    # Take first N words
    selected_words = words[:word_count]
    
    return " ".join(selected_words)


def sanitize_for_filename(text: str, max_length: int = 50) -> str:
    """
    Sanitize text for use as a filename.
    
    Removes special characters, converts to lowercase, replaces spaces with hyphens,
    and truncates to max length.
    
    Args:
        text: The text to sanitize
        max_length: Maximum length of the output (default: 50)
    
    Returns:
        Sanitized string safe for use in filenames
    
    Examples:
        >>> sanitize_for_filename("The Brave Little Dragon!")
        'the-brave-little-dragon'
        >>> sanitize_for_filename("Hello   World")
        'hello-world'
        >>> sanitize_for_filename("Test@#$%^&*()")
        'test'
    """
    if not text:
        return ""
    
    # Convert to lowercase
    result = text.lower()
    
    # Replace any non-alphanumeric characters (except spaces and hyphens) with empty string
    result = re.sub(r'[^a-z0-9\s-]', '', result)
    
    # Replace multiple spaces/hyphens with single hyphen
    result = re.sub(r'[\s-]+', '-', result)
    
    # Remove leading/trailing hyphens
    result = result.strip('-')
    
    # Truncate to max length, but avoid cutting mid-word if possible
    if len(result) > max_length:
        # Try to cut at a hyphen boundary
        truncated = result[:max_length]
        last_hyphen = truncated.rfind('-')
        
        # If there's a hyphen in the last 10 chars, cut there for cleaner result
        if last_hyphen > max_length - 10:
            result = truncated[:last_hyphen]
        else:
            result = truncated.rstrip('-')
    
    return result


def generate_descriptive_filename(
    text: str,
    max_length: int = 50,
    word_count: int = 6,
    use_ai: bool = False
) -> str:
    """
    Generate a descriptive filename from input text.
    
    Extracts the first few words from the text, sanitizes them for filesystem use,
    and returns a string suitable for use as a filename (without extension or UUID).
    
    Args:
        text: The input text to generate filename from
        max_length: Maximum length of the descriptive part (default: 50)
        word_count: Number of words to extract (default: 6)
        use_ai: If True, use AI summarization (Option B, not implemented)
    
    Returns:
        Sanitized filename string like 'once-upon-a-time-a-brave'
    
    Examples:
        >>> generate_descriptive_filename("Once upon a time, a brave dragon...")
        'once-upon-a-time-a-brave'
    """
    if use_ai:
        # Option B: AI-powered summarization (not implemented yet)
        # This would call Azure OpenAI to generate a meaningful title
        raise NotImplementedError("AI-powered filename generation not yet implemented")
    
    # Option A: Simple text extraction
    first_words = extract_first_words(text, word_count)
    sanitized = sanitize_for_filename(first_words, max_length)
    
    # Fallback if text produces empty result
    if not sanitized:
        sanitized = "audio"
    
    return sanitized


def generate_filename_with_uuid(
    text: str,
    max_length: int = 50,
    word_count: int = 6,
    extension: str = ".mp3"
) -> str:
    """
    Generate a complete filename with descriptive text and UUID suffix.
    
    Args:
        text: The input text to generate filename from
        max_length: Maximum length of the descriptive part (default: 50)
        word_count: Number of words to extract (default: 6)
        extension: File extension to append (default: ".mp3")
    
    Returns:
        Complete filename like 'once-upon-a-time-a-brave_a3b2c1d4.mp3'
    """
    descriptive = generate_descriptive_filename(text, max_length, word_count)
    short_uuid = str(uuid.uuid4())[:8]  # First 8 chars of UUID
    
    return f"{descriptive}_{short_uuid}{extension}"


def generate_synthesis_id(text: str, max_length: int = 50, word_count: int = 6) -> str:
    """
    Generate a synthesis ID with descriptive text and UUID suffix.
    
    This replaces the old pattern of 'story-{uuid}' with a more descriptive format.
    
    Args:
        text: The input text to generate ID from
        max_length: Maximum length of the descriptive part (default: 50)
        word_count: Number of words to extract (default: 6)
    
    Returns:
        Synthesis ID like 'once-upon-a-time-a-brave_a3b2c1d4'
    """
    descriptive = generate_descriptive_filename(text, max_length, word_count)
    short_uuid = str(uuid.uuid4())[:8]  # First 8 chars of UUID
    
    return f"{descriptive}_{short_uuid}"
