"""
Unit tests for markdown_utils module.

Tests all markdown cleaning functions to ensure text is properly
prepared for speech synthesis.
"""

import pytest
from markdown_utils import (
    remove_markdown_tables,
    remove_markdown_bullets,
    remove_markdown_headers,
    remove_markdown_emphasis,
    remove_markdown_links,
    remove_markdown_code_blocks,
    remove_markdown_horizontal_rules,
    remove_markdown_blockquotes,
    clean_markdown_for_speech
)


class TestRemoveMarkdownTables:
    """Tests for remove_markdown_tables function."""
    
    def test_removes_simple_table(self):
        """Test removal of a simple markdown table."""
        text = """Some text before.

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

Some text after."""
        
        result = remove_markdown_tables(text)
        assert "Header 1" not in result
        assert "Cell 1" not in result
        assert "|" not in result
        assert "Some text before." in result
        assert "Some text after." in result
    
    def test_removes_table_with_alignment(self):
        """Test removal of table with alignment markers."""
        text = """| Left | Center | Right |
|:-----|:------:|------:|
| A    | B      | C     |"""
        
        result = remove_markdown_tables(text)
        assert "|" not in result
        assert result.strip() == ""
    
    def test_preserves_non_table_text(self):
        """Test that non-table text is preserved."""
        text = "This is regular text without any tables."
        result = remove_markdown_tables(text)
        assert result == text
    
    def test_handles_empty_text(self):
        """Test handling of empty input."""
        assert remove_markdown_tables("") == ""
    
    def test_handles_pipe_in_text(self):
        """Test that pipes in regular text are preserved."""
        text = "The command is: ls | grep foo"
        result = remove_markdown_tables(text)
        # Single pipes in regular text should be preserved
        assert "ls | grep foo" in result


class TestRemoveMarkdownBullets:
    """Tests for remove_markdown_bullets function."""
    
    def test_removes_asterisk_bullets(self):
        """Test removal of * bullets."""
        text = """* Item one
* Item two
* Item three"""
        result = remove_markdown_bullets(text)
        assert "*" not in result
        assert "Item one" in result
        assert "Item two" in result
        assert "Item three" in result
    
    def test_removes_dash_bullets(self):
        """Test removal of - bullets."""
        text = """- First item
- Second item
- Third item"""
        result = remove_markdown_bullets(text)
        lines = result.strip().split('\n')
        assert "First item" in lines[0]
        assert "Second item" in lines[1]
        assert "Third item" in lines[2]
    
    def test_removes_plus_bullets(self):
        """Test removal of + bullets."""
        text = """+ Alpha
+ Beta
+ Gamma"""
        result = remove_markdown_bullets(text)
        assert "+" not in result
        assert "Alpha" in result
    
    def test_removes_numbered_list(self):
        """Test removal of numbered list items."""
        text = """1. First step
2. Second step
3. Third step"""
        result = remove_markdown_bullets(text)
        assert "1." not in result
        assert "First step" in result
        assert "Second step" in result
    
    def test_removes_numbered_list_with_parenthesis(self):
        """Test removal of numbered list items with )."""
        text = """1) One
2) Two
3) Three"""
        result = remove_markdown_bullets(text)
        assert "1)" not in result
        assert "One" in result
    
    def test_removes_nested_bullets(self):
        """Test handling of nested/indented bullets."""
        text = """* Main item
  * Sub item
  * Another sub item
* Another main item"""
        result = remove_markdown_bullets(text)
        assert "Main item" in result
        assert "Sub item" in result
    
    def test_removes_checkbox_items(self):
        """Test removal of checkbox list items."""
        text = """- [ ] Unchecked item
- [x] Checked item
- [X] Also checked"""
        result = remove_markdown_bullets(text)
        assert "[ ]" not in result
        assert "[x]" not in result
        assert "Unchecked item" in result
        assert "Checked item" in result
    
    def test_preserves_regular_text(self):
        """Test that regular text is preserved."""
        text = "This is just a normal paragraph."
        result = remove_markdown_bullets(text)
        assert result == text


class TestRemoveMarkdownHeaders:
    """Tests for remove_markdown_headers function."""
    
    def test_removes_h1(self):
        """Test removal of H1 header."""
        text = "# Main Title"
        result = remove_markdown_headers(text)
        assert "#" not in result
        assert "Main Title" in result
    
    def test_removes_h2(self):
        """Test removal of H2 header."""
        text = "## Section Title"
        result = remove_markdown_headers(text)
        assert "##" not in result
        assert "Section Title" in result
    
    def test_removes_h3_through_h6(self):
        """Test removal of H3-H6 headers."""
        text = """### Level 3
#### Level 4
##### Level 5
###### Level 6"""
        result = remove_markdown_headers(text)
        assert "#" not in result
        assert "Level 3" in result
        assert "Level 4" in result
        assert "Level 5" in result
        assert "Level 6" in result
    
    def test_preserves_hash_in_text(self):
        """Test that # in regular text is preserved."""
        text = "Use #hashtag for social media"
        result = remove_markdown_headers(text)
        assert result == text


class TestRemoveMarkdownEmphasis:
    """Tests for remove_markdown_emphasis function."""
    
    def test_removes_bold_asterisks(self):
        """Test removal of **bold** text."""
        text = "This is **bold** text."
        result = remove_markdown_emphasis(text)
        assert "**" not in result
        assert "bold" in result
    
    def test_removes_bold_underscores(self):
        """Test removal of __bold__ text."""
        text = "This is __bold__ text."
        result = remove_markdown_emphasis(text)
        assert "__" not in result
        assert "bold" in result
    
    def test_removes_italic_asterisks(self):
        """Test removal of *italic* text."""
        text = "This is *italic* text."
        result = remove_markdown_emphasis(text)
        assert result.count("*") == 0
        assert "italic" in result
    
    def test_removes_italic_underscores(self):
        """Test removal of _italic_ text."""
        text = "This is _italic_ text."
        result = remove_markdown_emphasis(text)
        # Underscores in isolation should be removed
        assert "italic" in result
    
    def test_removes_strikethrough(self):
        """Test removal of ~~strikethrough~~ text."""
        text = "This is ~~deleted~~ text."
        result = remove_markdown_emphasis(text)
        assert "~~" not in result
        assert "deleted" in result
    
    def test_removes_inline_code(self):
        """Test removal of `code` backticks."""
        text = "Use the `print()` function."
        result = remove_markdown_emphasis(text)
        assert "`" not in result
        assert "print()" in result
    
    def test_preserves_underscores_in_words(self):
        """Test that underscores in variable names are preserved."""
        text = "The variable_name is important."
        result = remove_markdown_emphasis(text)
        assert "variable_name" in result


class TestRemoveMarkdownLinks:
    """Tests for remove_markdown_links function."""
    
    def test_removes_inline_links(self):
        """Test removal of [text](url) links."""
        text = "Visit [Google](https://google.com) for more."
        result = remove_markdown_links(text)
        assert "](https://google.com)" not in result
        assert "Google" in result
        assert "[" not in result
    
    def test_removes_reference_links(self):
        """Test removal of [text][ref] links."""
        text = "See [documentation][docs] for details."
        result = remove_markdown_links(text)
        assert "documentation" in result
        assert "[docs]" not in result
    
    def test_removes_reference_definitions(self):
        """Test removal of [ref]: url definitions."""
        text = """Some text.

[google]: https://google.com

More text."""
        result = remove_markdown_links(text)
        assert "https://google.com" not in result
    
    def test_removes_images(self):
        """Test removal of ![alt](url) images."""
        text = "Here is an image: ![Logo](logo.png)"
        result = remove_markdown_links(text)
        assert "logo.png" not in result
        assert "![" not in result
        # Alt text should be preserved
        assert "Logo" in result


class TestRemoveMarkdownCodeBlocks:
    """Tests for remove_markdown_code_blocks function."""
    
    def test_removes_fenced_code_block(self):
        """Test removal of ``` code blocks."""
        text = """Some text.

```python
def hello():
    print("Hello")
```

More text."""
        result = remove_markdown_code_blocks(text)
        assert "```" not in result
        assert "def hello():" not in result
        assert "Some text." in result
        assert "More text." in result
    
    def test_removes_fenced_code_block_no_language(self):
        """Test removal of ``` blocks without language."""
        text = """Text before.

```
some code
```

Text after."""
        result = remove_markdown_code_blocks(text)
        assert "```" not in result
        assert "some code" not in result
    
    def test_preserves_non_code_text(self):
        """Test that regular text is preserved."""
        text = "No code blocks here."
        result = remove_markdown_code_blocks(text)
        assert result == text


class TestRemoveMarkdownHorizontalRules:
    """Tests for remove_markdown_horizontal_rules function."""
    
    def test_removes_dash_rule(self):
        """Test removal of --- horizontal rule."""
        text = "Before.\n---\nAfter."
        result = remove_markdown_horizontal_rules(text)
        assert "---" not in result
        assert "Before." in result
        assert "After." in result
    
    def test_removes_asterisk_rule(self):
        """Test removal of *** horizontal rule."""
        text = "Before.\n***\nAfter."
        result = remove_markdown_horizontal_rules(text)
        assert "***" not in result
    
    def test_removes_underscore_rule(self):
        """Test removal of ___ horizontal rule."""
        text = "Before.\n___\nAfter."
        result = remove_markdown_horizontal_rules(text)
        assert "___" not in result
    
    def test_removes_long_rules(self):
        """Test removal of longer rules."""
        text = "Before.\n-----------\nAfter."
        result = remove_markdown_horizontal_rules(text)
        assert "-----------" not in result


class TestRemoveMarkdownBlockquotes:
    """Tests for remove_markdown_blockquotes function."""
    
    def test_removes_single_blockquote(self):
        """Test removal of > blockquote."""
        text = "> This is quoted text."
        result = remove_markdown_blockquotes(text)
        assert ">" not in result
        assert "This is quoted text." in result
    
    def test_removes_multi_line_blockquote(self):
        """Test removal of multi-line blockquote."""
        text = """> First line
> Second line
> Third line"""
        result = remove_markdown_blockquotes(text)
        assert ">" not in result
        assert "First line" in result
        assert "Second line" in result
        assert "Third line" in result
    
    def test_removes_nested_blockquote(self):
        """Test handling of nested blockquotes."""
        text = "> Outer quote\n>> Inner quote"
        result = remove_markdown_blockquotes(text)
        # At least outer > should be removed
        assert "Outer quote" in result
    
    def test_preserves_non_blockquote_text(self):
        """Test that regular text is preserved."""
        text = "Not a blockquote."
        result = remove_markdown_blockquotes(text)
        assert result == text


class TestCleanMarkdownForSpeech:
    """Tests for the main clean_markdown_for_speech function."""
    
    def test_cleans_mixed_markdown(self):
        """Test cleaning of text with multiple markdown elements."""
        text = """# The Adventure

Once upon a time, there was a **brave** knight.

## Characters

- Sir Lancelot
- Princess Luna
- The Dragon

He said: "I will save you!"

---

The end."""
        
        result = clean_markdown_for_speech(text)
        
        # Headers should be plain text
        assert "The Adventure" in result
        assert "#" not in result
        
        # Bold should be removed
        assert "**" not in result
        assert "brave" in result
        
        # Bullets should be removed
        assert "-" not in result or result.count("-") == 0
        assert "Sir Lancelot" in result
        
        # Horizontal rules should be removed
        assert "---" not in result
    
    def test_cleans_story_with_table(self):
        """Test cleaning of story with a table that should be ignored."""
        text = """Story: The Magic Garden

| Character | Role |
|-----------|------|
| Alice     | Hero |
| Bob       | Villain |

Once upon a time, Alice walked into the garden."""
        
        result = clean_markdown_for_speech(text)
        
        # Table should be removed
        assert "|" not in result
        assert "Character" not in result
        assert "Hero" not in result
        
        # Story text should remain
        assert "Story: The Magic Garden" in result
        assert "Once upon a time, Alice walked into the garden." in result
    
    def test_handles_empty_input(self):
        """Test handling of empty input."""
        assert clean_markdown_for_speech("") == ""
        assert clean_markdown_for_speech(None) is None
    
    def test_handles_plain_text(self):
        """Test that plain text passes through unchanged."""
        text = "This is just plain text without any markdown."
        result = clean_markdown_for_speech(text)
        assert result == text
    
    def test_cleans_code_blocks_before_other_elements(self):
        """Test that code blocks are removed before other processing."""
        text = """# Header

```python
# This is code, not a header
* This is not a list
```

* This IS a list item"""
        
        result = clean_markdown_for_speech(text)
        
        # Code block content should be gone
        assert "# This is code" not in result
        assert "* This is not a list" not in result
        
        # Real header should be cleaned
        assert "Header" in result
        assert "#" not in result
        
        # Real list item should be cleaned
        assert "This IS a list item" in result
    
    def test_preserves_dialogue(self):
        """Test that dialogue punctuation is preserved."""
        text = '"Hello," said the rabbit. "How are you?"'
        result = clean_markdown_for_speech(text)
        assert '"Hello,"' in result
        assert "said the rabbit" in result
    
    def test_collapses_excessive_whitespace(self):
        """Test that excessive whitespace is collapsed."""
        text = """Line one.



Line two with    extra   spaces."""
        
        result = clean_markdown_for_speech(text)
        
        # Should not have more than 2 consecutive blank lines
        assert "\n\n\n\n" not in result
        
        # Extra spaces should be collapsed
        assert "extra spaces" in result or "extra   spaces" not in result


class TestRealWorldExamples:
    """Test with real-world markdown examples."""
    
    def test_bedtime_story_with_markdown(self):
        """Test cleaning a typical bedtime story with markdown formatting."""
        story = """# The Sleepy Bear

**Chapter 1: A Cozy Den**

Once upon a time, in a forest far away, there lived a little bear named *Bruno*.

Bruno had many friends:
- Oliver the Owl
- Ruby the Rabbit
- Felix the Fox

## What Happened Next

> "Time for bed," said Bruno's mother.

Bruno yawned and stretched. He was very tired after a long day of adventures.

---

*The End*

| Time | Activity |
|------|----------|
| 8pm  | Bedtime  |
"""
        
        result = clean_markdown_for_speech(story)
        
        # All markdown should be cleaned
        assert "#" not in result
        assert "**" not in result
        assert "*Bruno*" not in result
        assert "Bruno" in result  # Text preserved
        assert "- Oliver" not in result
        assert "Oliver the Owl" in result  # List item text preserved
        assert "|" not in result  # Table removed
        assert "8pm" not in result  # Table content removed
        
        # Story content should be preserved
        assert "The Sleepy Bear" in result
        assert "Once upon a time" in result
        assert "Time for bed" in result
        assert "The End" in result
    
    def test_ios_shortcut_formatted_text(self):
        """Test cleaning text that might come from iOS shortcuts."""
        text = """Here's a recipe:

**Ingredients:**
* 2 cups flour
* 1 cup sugar
* 3 eggs

**Instructions:**
1. Mix the dry ingredients
2. Add the eggs
3. Bake at 350°F

Enjoy your cake!"""
        
        result = clean_markdown_for_speech(text)
        
        # Bullets and numbers should be cleaned
        assert "* 2 cups" not in result
        assert "2 cups flour" in result
        assert "1. Mix" not in result
        assert "Mix the dry ingredients" in result
        
        # Bold headers should be cleaned
        assert "**" not in result
        assert "Ingredients:" in result
        assert "Instructions:" in result
