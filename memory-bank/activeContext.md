# Active Context - Toni TTS

## Current Work Focus
Intelligent file naming feature implemented and deployed. Project is in a stable, enhanced state.

## Recent Changes
- **Intelligent File Naming**: Implemented Option A (simple text extraction) for descriptive audio filenames
  - New `filename_utils.py` module with text extraction and sanitization functions
  - Audio files now named like `hello-world-this-is-a-test_6bf47a18.mp3` instead of `story_uuid.mp3`
  - Configuration constants added to `story_config.py`
  - Both `batch_start()` and `sync_tts()` updated to use descriptive names
- **Code Cleanup**: Removed 9 unused files (LAB2*.md, test MP3s, function_app_old.py)
- **Deployed**: Changes deployed and verified working in Azure Portal

## Project Status
✅ **Stable and Deployed with Enhanced Features**

The project is fully functional with:
- 3 API endpoints operational (`batch-start`, `batch-check`, `sync-tts`)
- **NEW**: Intelligent file naming for all audio output
- Azure Functions deployed to West US 3
- Speech Service configured in East US
- Blob Storage ready for audio files

## Active Decisions and Considerations

### Current Defaults
- **Voice**: `en-US-GuyNeural` (male, good for narration)
- **Style**: `hopeful` (positive, faith-filled tone)
- **Audio Format**: 24kHz, 96kbps mono MP3
- **SAS URL Expiry**: 48 hours
- **Filename Max Length**: 50 characters (before UUID)
- **Filename Word Count**: 6 words extracted from text

### Architecture Decisions
- Using async batch synthesis for all long texts
- Internal polling in `batch-check` (3 min max) to simplify iOS Shortcuts
- Pre-signed SAS URLs for audio download (works with Shortcuts)
- Descriptive filenames with 8-char UUID suffix for uniqueness

## Important Patterns and Preferences

### Code Style
- Python with type hints where beneficial
- Comprehensive logging for debugging
- Environment variables for all configuration
- Detailed error responses with context
- Utility modules for reusable functionality (`filename_utils.py`)

### API Design
- REST endpoints with JSON responses
- Function-level authentication (API keys)
- Descriptive error messages
- Status codes follow HTTP conventions

### Filename Generation Pattern
- Extract first N words from input text
- Sanitize: lowercase, remove special chars, hyphen-delimited
- Append 8-char UUID suffix for uniqueness
- Example: "Once upon a time" → `once-upon-a-time-a-brave_a3b2c1d4.mp3`

## Next Steps (When Development Resumes)
1. No immediate tasks - project is stable with enhanced features
2. Potential future enhancements:
   - Option B: AI-powered title generation (Azure OpenAI)
   - Queue-based processing for reliability
   - WebSocket updates for real-time progress
   - Voice cloning support
   - SSML editor for advanced markup
   - Caching for frequently requested texts
   - Rate limiting

## Learnings and Project Insights

### What Works Well
- Batch Synthesis API handles long texts reliably
- Pre-signed URLs integrate well with iOS Shortcuts
- Internal polling simplifies client implementation
- Low cost (~$1-5/month for personal use)
- Descriptive filenames make audio files easily identifiable

### Known Considerations
- Synthesis can take 1-3 minutes for long stories
- Timeout after 3 minutes if synthesis takes too long
- Need to manage blob storage cleanup manually
- Some voices don't support all speaking styles

## Environment Notes
- Local development requires `local.settings.json` (not in git)
- Azure CLI needed for deployment and management
- Function keys required for API access
- Deploy command: `func azure functionapp publish tonisynthfunc`
