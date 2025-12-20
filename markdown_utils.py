"""
Markdown utilities for text-to-speech processing.

This module provides functions to clean markdown formatting from text
before converting it to speech. Tables are removed, and bullets/lists
are converted to plain text for natural reading.
"""

import re
from typing import List, Tuple


def remove_markdown_tables(text: str) -> str:
    """
    Remove markdown tables from text.
    
    Tables typically have this format:
    | Header 1 | Header 2 |
    |----------|----------|
    | Cell 1   | Cell 2   |
    
    Args:
        text: Input text potentially containing markdown tables
        
    Returns:
        Text with tables removed
    """
    lines = text.split('\n')
    result_lines = []
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check if line is a table row (starts and ends with | or contains | separated cells)
        is_table_row = bool(re.match(r'^\|.*\|$', stripped))
        
        # Check if line is a table separator (|---|---|)
        is_table_separator = bool(re.match(r'^\|[\s\-:|]+\|$', stripped))
        
        if is_table_row or is_table_separator:
            in_table = True
            continue  # Skip table lines
        
        # If we were in a table and hit a non-table line, we've exited the table
        if in_table and stripped:
            in_table = False
        
        result_lines.append(line)
    
    # Clean up extra blank lines that might be left after table removal
    return _collapse_blank_lines(result_lines)


def remove_markdown_bullets(text: str) -> str:
    """
    Remove markdown bullet points and convert to plain sentences.
    
    Supports:
    - Unordered lists: *, -, +
    - Ordered lists: 1., 2., etc.
    - Nested lists (removes indentation)
    - Checkbox lists: [ ], [x], [X]
    
    Args:
        text: Input text with markdown bullets
        
    Returns:
        Text with bullets removed, formatted as plain sentences
    """
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Remove leading whitespace for processing
        stripped = line.lstrip()
        
        # Match checkbox list items FIRST: - [ ] item, - [x] item, etc.
        # Must check before regular unordered list to avoid partial match
        checkbox_match = re.match(r'^[\*\-\+]\s+\[[xX\s]\]\s+(.+)$', stripped)
        if checkbox_match:
            content = checkbox_match.group(1).strip()
            result_lines.append(content)
            continue
        
        # Match unordered list items: *, -, +
        unordered_match = re.match(r'^[\*\-\+]\s+(.+)$', stripped)
        if unordered_match:
            content = unordered_match.group(1).strip()
            result_lines.append(content)
            continue
        
        # Match ordered list items: 1., 2., etc.
        ordered_match = re.match(r'^\d+[\.\)]\s+(.+)$', stripped)
        if ordered_match:
            content = ordered_match.group(1).strip()
            result_lines.append(content)
            continue
            continue
        
        # Keep non-list lines as-is
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def remove_markdown_headers(text: str) -> str:
    """
    Convert markdown headers to plain text.
    
    Removes # symbols from headers like:
    # Header 1
    ## Header 2
    ### Header 3
    
    Args:
        text: Input text with markdown headers
        
    Returns:
        Text with headers converted to plain text
    """
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Match header lines: # Header, ## Header, etc.
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            content = header_match.group(2).strip()
            result_lines.append(content)
            continue
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def remove_markdown_emphasis(text: str) -> str:
    """
    Remove markdown emphasis markers (bold, italic, strikethrough).
    
    Handles:
    - **bold** or __bold__
    - *italic* or _italic_
    - ~~strikethrough~~
    - `code`
    
    Args:
        text: Input text with markdown emphasis
        
    Returns:
        Text with emphasis markers removed
    """
    # Remove bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove italic: *text* or _text_ (careful not to affect underscores in words)
    text = re.sub(r'(?<!\w)\*([^\*]+?)\*(?!\w)', r'\1', text)
    text = re.sub(r'(?<!\w)_([^_]+?)_(?!\w)', r'\1', text)
    
    # Remove strikethrough: ~~text~~
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    
    # Remove inline code: `code`
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    return text


def remove_markdown_links(text: str) -> str:
    """
    Convert markdown links to just the link text.
    
    [link text](url) -> link text
    [link text][reference] -> link text
    
    Args:
        text: Input text with markdown links
        
    Returns:
        Text with only link text preserved
    """
    # Remove inline links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove reference links: [text][ref]
    text = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', text)
    
    # Remove reference definitions: [ref]: url
    text = re.sub(r'^\[[^\]]+\]:\s*.+$', '', text, flags=re.MULTILINE)
    
    # Remove images: ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    
    return text


def remove_markdown_code_blocks(text: str) -> str:
    """
    Remove markdown code blocks.
    
    Handles:
    - Fenced code blocks (```)
    - Indented code blocks (4 spaces or 1 tab)
    
    Args:
        text: Input text with markdown code blocks
        
    Returns:
        Text with code blocks removed
    """
    # Remove fenced code blocks: ```language\ncode\n```
    text = re.sub(r'```[\w]*\n.*?```', '', text, flags=re.DOTALL)
    
    # Note: We keep indented lines as they might be intentional formatting
    # Only remove if they're clearly code blocks (consecutive 4+ space indented lines)
    
    return text


def remove_markdown_horizontal_rules(text: str) -> str:
    """
    Remove markdown horizontal rules.
    
    Handles: ---, ***, ___ (3 or more)
    
    Args:
        text: Input text with horizontal rules
        
    Returns:
        Text with horizontal rules removed
    """
    # Remove horizontal rules: --- or *** or ___ (3 or more characters)
    text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    return text


def remove_markdown_blockquotes(text: str) -> str:
    """
    Convert markdown blockquotes to plain text.
    
    > quoted text -> quoted text
    
    Args:
        text: Input text with blockquotes
        
    Returns:
        Text with blockquote markers removed
    """
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Remove blockquote markers: > text
        blockquote_match = re.match(r'^>\s*(.*)$', line)
        if blockquote_match:
            content = blockquote_match.group(1)
            result_lines.append(content)
            continue
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def clean_markdown_for_speech(text: str) -> str:
    """
    Clean all markdown formatting from text for natural speech synthesis.
    
    This is the main function to use. It applies all cleaning functions
    in the correct order to produce clean, readable text.
    
    Processing order:
    1. Remove code blocks (before other processing to avoid false matches)
    2. Remove tables
    3. Remove horizontal rules
    4. Remove headers (keep the text)
    5. Remove blockquotes (keep the text)
    6. Remove bullets/lists (keep the text)
    7. Remove links (keep link text)
    8. Remove emphasis markers (keep the text)
    9. Clean up whitespace
    
    Args:
        text: Input text with markdown formatting
        
    Returns:
        Clean text suitable for speech synthesis
    """
    if not text:
        return text
    
    # Apply cleaning functions in order
    text = remove_markdown_code_blocks(text)
    text = remove_markdown_tables(text)
    text = remove_markdown_horizontal_rules(text)
    text = remove_markdown_headers(text)
    text = remove_markdown_blockquotes(text)
    text = remove_markdown_bullets(text)
    text = remove_markdown_links(text)
    text = remove_markdown_emphasis(text)
    
    # Final cleanup
    text = _clean_whitespace(text)
    
    return text


def _collapse_blank_lines(lines: List[str]) -> str:
    """
    Collapse multiple consecutive blank lines into at most two.
    
    Args:
        lines: List of text lines
        
    Returns:
        Text with collapsed blank lines
    """
    result_lines = []
    blank_count = 0
    
    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 2:
                result_lines.append(line)
        else:
            blank_count = 0
            result_lines.append(line)
    
    return '\n'.join(result_lines)


def _clean_whitespace(text: str) -> str:
    """
    Clean up whitespace in text.
    
    - Collapse multiple spaces to single space
    - Collapse multiple blank lines to max 2
    - Strip trailing whitespace from lines
    - Strip leading/trailing whitespace from text
    
    Args:
        text: Input text
        
    Returns:
        Text with cleaned whitespace
    """
    lines = text.split('\n')
    
    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in lines]
    
    # Collapse multiple blank lines
    text = _collapse_blank_lines(lines)
    
    # Collapse multiple spaces within lines (but preserve newlines)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Strip leading/trailing whitespace from entire text
    text = text.strip()
    
    return text
