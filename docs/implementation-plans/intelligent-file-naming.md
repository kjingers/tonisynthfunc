# Implementation Plan: Intelligent File Naming for Audio Output

## [Overview]

Add intelligent file naming to the TTS function so output MP3 files have descriptive names based on the input text content, rather than generic UUID-only names like `story-abc123.mp3`.

This feature improves user experience by making audio files easily identifiable in storage and downloads. For example, a bedtime story about a dragon would be named `the-brave-little-dragon_a3b2c1.mp3` instead of `story-a3b2c1d4-5e6f-7890.mp3`.

The plan covers two implementation approaches:
- **Option A (Simple)**: Extract and sanitize first N words from input text
- **Option B (AI-Powered)**: Use Azure OpenAI to generate a meaningful title

Both options maintain backward compatibility and include a UUID suffix for uniqueness.

---

## [Types]

New type definitions for filename generation configuration and utilities.

### Configuration Constants (in `story_config.py`)

```python
# Filename generation settings
FILENAME_MAX_LENGTH = 50           # Max chars for descriptive part (before UUID)
FILENAME_WORD_COUNT = 6            # Max words to extract (Option A)
FILENAME_USE_AI = False            # Toggle AI summarization (Option B)
FILENAME_AI_MAX_TOKENS = 10        # Max tokens for AI-generated title
```

### Helper Function Return Type

```python
def generate_descriptive_filename(text: str, use_ai: bool = False) -> str:
    """
    Returns a sanitized filename string like 'the-brave-little-dragon'
    Does NOT include extension or UUID suffix
    """
    pass
```

---

## [Files]

### Files to Modify

| File | Changes |
|------|---------|
| `function_app.py` | Import filename helper, update `batch_start()` and `batch_check()` to use descriptive names |
| `story_config.py` | Add filename configuration constants |

### Files to Create

| File | Purpose |
|------|---------|
| `filename_utils.py` | New module containing filename generation logic |
| `docs/implementation-plans/intelligent-file-naming.md` | This implementation plan |

### Files to Delete (Cleanup)

| File | Reason |
|------|--------|
| `LAB2_PAGE1.md` | Unrelated Azure Foundry lab content |
| `LAB2_PAGE2.md` | Unrelated Azure Foundry lab content |
| `LAB2_PAGE3.md` | Unrelated Azure Foundry lab content |
| `function_app_old.py` | Deprecated version of function_app.py |
| `bedtime-story-test.mp3` | Test file, not needed in repo |
| `cheerful-style.mp3` | Test file, not needed in repo |
| `excited-style.mp3` | Test file, not needed in repo |
| `expressive-bedtime-story.mp3` | Test file, not needed in repo |
| `test-audio.mp3` | Test file, not needed in repo |

---

## [Functions]

### New Functions

#### `filename_utils.py`

| Function | Signature | Purpose |
|----------|-----------|---------|
| `generate_descriptive_filename` | `(text: str, max_length: int = 50, use_ai: bool = False) -> str` | Main entry point for filename generation |
| `extract_first_words` | `(text: str, word_count: int = 6) -> str` | Extract first N words from text (Option A) |
| `sanitize_for_filename` | `(text: str, max_length: int = 50) -> str` | Remove special chars, lowercase, replace spaces with hyphens |
| `generate_ai_title` | `(text: str, max_tokens: int = 10) -> str` | Call Azure OpenAI for title (Option B) |

### Modified Functions

#### `function_app.py`

| Function | Current Behavior | New Behavior |
|----------|------------------|--------------|
| `batch_start()` | `synthesis_id = f"story-{uuid.uuid4()}"` | `synthesis_id = f"{descriptive_name}_{short_uuid}"` |
| `batch_check()` | Uses `synthesis_id` directly for filename | No changes needed (uses synthesis_id) |
| `sync_tts()` | `audio_filename = f"story_{uuid.uuid4()}.mp3"` | `audio_filename = f"{descriptive_name}_{short_uuid}.mp3"` |

---

## [Classes]

No new classes required. This feature uses utility functions only.

---

## [Dependencies]

### Option A (Simple) - No New Dependencies

No additional packages required. Uses only Python standard library:
- `re` (regex for sanitization)
- `uuid` (already imported)

### Option B (AI-Powered) - New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | `>=1.0.0` | Azure OpenAI client for title generation |

**Additional Azure Resources Required (Option B only):**
- Azure OpenAI Service resource
- GPT-4o-mini or GPT-3.5-turbo deployment
- New environment variables: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT`

---

## [Testing]

### Test Cases for `filename_utils.py`

```python
# test_filename_utils.py

def test_extract_first_words():
    """Test word extraction from various text inputs"""
    assert extract_first_words("Once upon a time there was a dragon") == "Once upon a time there was"
    assert extract_first_words("Short") == "Short"
    assert extract_first_words("") == ""

def test_sanitize_for_filename():
    """Test filename sanitization"""
    assert sanitize_for_filename("The Brave Little Dragon!") == "the-brave-little-dragon"
    assert sanitize_for_filename("Hello   World") == "hello-world"
    assert sanitize_for_filename("Test@#$%^&*()") == "test"
    assert sanitize_for_filename("a" * 100, max_length=50) == "a" * 50

def test_generate_descriptive_filename():
    """Test full filename generation"""
    result = generate_descriptive_filename("Once upon a time, a brave dragon...")
    assert result == "once-upon-a-time-a-brave"
    assert len(result) <= 50
```

### Integration Testing

1. Call `/api/batch-start` with a test story
2. Verify `synthesis_id` contains descriptive text
3. Verify audio file is uploaded with correct name
4. Verify SAS URL contains the descriptive filename

---

## [Implementation Order]

Sequential steps to implement this feature safely.

### Phase 1: Cleanup (Pre-requisite)
1. Delete unrelated files (LAB2*.md, *.mp3, function_app_old.py)
2. Commit cleanup changes

### Phase 2: Option A Implementation (Simple)
3. Create `filename_utils.py` with `extract_first_words()` and `sanitize_for_filename()`
4. Add configuration constants to `story_config.py`
5. Update `batch_start()` in `function_app.py` to use descriptive filenames
6. Update `sync_tts()` in `function_app.py` to use descriptive filenames
7. Test locally with sample texts
8. Deploy and verify in Azure

### Phase 3: Option B Implementation (AI-Powered) - Optional
9. Add `openai` to `requirements.txt`
10. Add Azure OpenAI environment variables to `local.settings.json`
11. Implement `generate_ai_title()` in `filename_utils.py`
12. Add `FILENAME_USE_AI` toggle to `story_config.py`
13. Update `generate_descriptive_filename()` to conditionally use AI
14. Test with AI enabled
15. Deploy and verify

---

## Design Trade-offs

### Option A: Simple Text Extraction

| Pros | Cons |
|------|------|
| Zero additional cost | May include generic phrases like "Once upon a time" |
| No external API calls | Less intelligent/meaningful |
| Instant, no latency | Word boundaries may be awkward |
| No new dependencies | Doesn't understand context |
| Works offline | May repeat similar names for similar stories |

**Best for:** Personal use, cost-conscious deployments, simplicity

### Option B: AI-Powered Summarization

| Pros | Cons |
|------|------|
| Smarter, more descriptive titles | Additional cost (~$0.001 per request) |
| Understands context | Adds 100-500ms latency |
| Can skip generic phrases | Requires Azure OpenAI resource setup |
| More unique names | New dependency and complexity |
| Better for large libraries | May occasionally generate odd titles |

**Best for:** Production deployments, large story libraries, premium experience

### Recommendation

**Start with Option A** (simple extraction). It provides 80% of the benefit with 0% additional cost or complexity. Option B can be added later as an enhancement if smarter naming is needed.

---

## Example Output

### Before (Current)
```
story-a3b2c1d4-5e6f-7890-abcd-1234567890ab.mp3
story_b4c3d2e1-6f7a-8901-bcde-2345678901bc.mp3
```

### After (Option A - Simple)
```
once-upon-a-time-in_a3b2c1d4.mp3
the-brave-little-dragon_b4c3d2e1.mp3
in-a-magical-forest_c5d4e3f2.mp3
```

### After (Option B - AI-Powered)
```
brave-dragon-adventure_a3b2c1d4.mp3
magical-forest-friends_b4c3d2e1.mp3
bedtime-princess-story_c5d4e3f2.mp3
```

---

## Configuration Reference

### story_config.py additions

```python
# ===========================================
# Filename Generation Settings
# ===========================================

# Maximum length of descriptive part (before UUID suffix)
FILENAME_MAX_LENGTH = 50

# Number of words to extract from text (Option A)
FILENAME_WORD_COUNT = 6

# Enable AI-powered title generation (Option B)
# Requires Azure OpenAI configuration
FILENAME_USE_AI = False

# Max tokens for AI-generated title (Option B)
FILENAME_AI_MAX_TOKENS = 10
```

### Environment Variables (Option B only)

```json
{
  "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
  "AZURE_OPENAI_KEY": "your-api-key",
  "AZURE_OPENAI_DEPLOYMENT": "gpt-4o-mini"
}
```

---

## Rollback Plan

If issues occur after deployment:

1. **Quick fix**: Set `FILENAME_USE_AI = False` in config (disables AI, falls back to simple)
2. **Full rollback**: Revert `function_app.py` changes, filenames return to UUID-only format
3. **Partial rollback**: Keep utility functions but don't call them (change one line in batch_start/sync_tts)

All options maintain backward compatibility - existing audio files and URLs remain valid.
