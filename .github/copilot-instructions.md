# GitHub Copilot Instructions for ToniSynthFunc

This file provides context and guidelines for GitHub Copilot when working with this repository.

## Project Overview

ToniSynthFunc is an Azure Functions-based Text-to-Speech API designed for generating audio files from text, with special support for bedtime stories featuring multiple character voices.

### Key Features
- **Batch synthesis** (`/batch-start`, `/batch-check`) - For long texts like bedtime stories
- **Synchronous TTS** (`/sync-tts`) - For shorter texts up to 5000 characters
- **Character voice detection** - Automatic dialogue parsing with multi-voice support
- **Adventure mode auto-detection** - Automatically enables character voices for stories
- **Markdown cleaning** - Removes formatting for natural speech synthesis

## Project Structure

```
tonisynthfunc/
├── function_app.py          # Main Azure Functions HTTP endpoints
├── character_voices.py      # Dialogue parsing and voice assignment
├── validators.py            # Input validation functions
├── markdown_utils.py        # Markdown cleaning for TTS
├── filename_utils.py        # Filename generation utilities
├── story_config.py          # Voice/style configuration and presets
├── http_helpers.py          # HTTP response helpers
├── exceptions.py            # Custom exception classes
├── logging_config.py        # Structured logging utilities
├── azure_clients.py         # Azure service client creation
├── storage_cleanup.py       # Storage cleanup utilities
├── tests/                   # Unit tests (pytest)
│   ├── test_*.py           # Test files for each module
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # CI/CD pipeline
├── API_DOCUMENTATION.md     # API reference documentation
└── requirements.txt         # Python dependencies
```

## Code Style Guidelines

### Python Standards
- Use **Python 3.11+** features and syntax
- Include **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes
- Follow **PEP 8** style guidelines
- Use **f-strings** for string formatting

### Function Structure
```python
def function_name(param1: str, param2: int = 0) -> dict:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        Description of return value
        
    Raises:
        ValidationError: When input validation fails
    """
    # Implementation
```

### Error Handling
- Use custom exceptions from `exceptions.py` (e.g., `ValidationError`, `SpeechServiceError`)
- Use HTTP helpers from `http_helpers.py` for consistent API responses
- Always log errors with context using `logging` module

### Testing
- Write tests in `tests/` directory using pytest
- Name test files as `test_<module_name>.py`
- Use descriptive test class and method names
- Test both success and error cases

## Azure Functions Patterns

### HTTP Triggers
```python
@app.route(route="endpoint-name", methods=["POST"])
def endpoint_name(req: func.HttpRequest) -> func.HttpResponse:
    """Endpoint description."""
    logging.info('Route hit: endpoint-name')
    
    try:
        req_body = req.get_json()
        # Validate inputs using validators.py
        # Process request
        # Return response using http_helpers.py
    except Exception as e:
        logging.error(f"Error: {str(e)}", exc_info=True)
        return error_response(str(e))
```

### Environment Variables
Required environment variables (defined in `local.settings.json` for local dev):
- `SPEECH_SERVICE_KEY` - Azure Cognitive Services Speech key
- `SPEECH_SERVICE_REGION` - Azure region (e.g., "westus2")
- `STORAGE_ACCOUNT_NAME` - Azure Storage account name
- `STORAGE_ACCOUNT_KEY` - Azure Storage account key
- `STORAGE_CONTAINER_NAME` - Blob container for audio files

## Key Implementation Patterns

### Input Validation
Always validate inputs using `validators.py`:
```python
from validators import validate_batch_start_request

validation = validate_batch_start_request(text=text, voice=voice, style=style)
if not validation.is_valid:
    return validation_error(validation.error, validation.field)
```

### SSML Generation
For text-to-speech, use SSML from `character_voices.py`:
```python
from character_voices import generate_character_ssml, generate_simple_ssml

if enable_character_voices:
    ssml = generate_character_ssml(text, narrator_voice, narrator_style)
else:
    ssml = generate_simple_ssml(text, voice, style)
```

### Markdown Cleaning
Clean markdown before TTS processing:
```python
from markdown_utils import clean_markdown_for_speech

text = clean_markdown_for_speech(text)
```

## Common Tasks

### Adding a New Endpoint
1. Add the route decorator and function in `function_app.py`
2. Create validators in `validators.py` if needed
3. Add unit tests in `tests/test_function_app.py`
4. Update `API_DOCUMENTATION.md`

### Adding a New Voice/Style
1. Update `story_config.py` with the new voice configuration
2. Add to `VOICE_STYLES` dict with supported styles
3. Update `STORY_PRESETS` if applicable
4. Update `API_DOCUMENTATION.md`

### Adding a New Character Voice Feature
1. Update `character_voices.py` for detection/parsing logic
2. Add tests in `tests/test_character_voices.py`
3. Update function_app.py to use the new feature

## Testing Commands

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_character_voices.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Dependencies

Key dependencies (see `requirements.txt`):
- `azure-functions` - Azure Functions runtime
- `azure-storage-blob` - Azure Blob Storage SDK
- `requests` - HTTP client for Azure Speech API
- `pytest` - Testing framework

## API Reference

See `API_DOCUMENTATION.md` for complete API documentation including:
- Endpoint specifications
- Request/response formats
- Available voices and styles
- Character voice configuration
- Error codes

## Notes for Copilot

When generating code for this project:
1. **Always use type hints** - This codebase has full type annotation
2. **Use existing utilities** - Check `validators.py`, `http_helpers.py`, `exceptions.py` before writing new helpers
3. **Follow the logging pattern** - Use `logging.info()` for route hits and important events
4. **Write tests** - New features should include tests in the `tests/` directory
5. **Update documentation** - Keep `API_DOCUMENTATION.md` in sync with changes
6. **Handle errors gracefully** - Use the custom exception hierarchy
