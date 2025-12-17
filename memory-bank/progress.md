# Progress - Toni TTS

## What Works

### Core Functionality ✅
- **Batch Synthesis** (`/api/batch-start`): Accepts text, starts Azure batch synthesis job
- **Status Check** (`/api/batch-check`): Polls synthesis status, uploads audio to blob storage
- **Sync TTS** (`/api/sync-tts`): Legacy synchronous endpoint for short texts
- **Intelligent File Naming** ✨ NEW: Descriptive filenames based on input text

### Infrastructure ✅
- Azure Functions deployed and running (West US 3)
- Azure Speech Service configured (East US)
- Azure Blob Storage ready (container: `audiofilestoni`)
- Pre-signed SAS URL generation working

### Configuration ✅
- Voice/style configuration separated into `story_config.py`
- Filename configuration constants for intelligent naming
- Multiple neural voices supported (16+)
- Expressive speaking styles available
- Customizable audio format

### Documentation ✅
- README.md with comprehensive overview
- DEVELOPMENT.md with setup and deployment guide
- iOS_SHORTCUTS_SETUP.md for Apple Shortcuts integration
- BEDTIME_STORIES_GUIDE.md for usage guide
- Implementation plans in `docs/implementation-plans/`
- Memory Bank initialized

## What's Left to Build

### Potential Enhancements (Not Planned)
These are ideas for future development, not current requirements:

1. **AI-Powered Title Generation (Option B)**
   - Use Azure OpenAI to generate creative titles
   - Placeholder exists in `filename_utils.py`
   - Status: Not started (Option A implemented)

2. **Queue-based Processing**
   - Replace direct API calls with Azure Queue
   - Better reliability for high volume
   - Status: Not started, not needed for personal use

3. **WebSocket Updates**
   - Real-time synthesis progress
   - Better UX for web app
   - Status: Not started

4. **Voice Cloning**
   - Custom neural voice support
   - Configuration exists but not tested
   - Status: Placeholder code exists

5. **SSML Editor**
   - Advanced speech markup editing
   - Prosody, emphasis control
   - Status: Not started

6. **Caching**
   - Cache frequently requested texts
   - Reduce synthesis costs
   - Status: Not started

7. **Rate Limiting**
   - Prevent abuse
   - Control costs
   - Status: Not started

## Current Status

### Project State: 🟢 STABLE & ENHANCED

The project is fully functional with the new intelligent file naming feature deployed:

| Feature | Status | Notes |
|---------|--------|-------|
| Batch synthesis | ✅ Working | Handles 30+ min stories |
| Status polling | ✅ Working | 3 min internal polling |
| Audio storage | ✅ Working | Blob storage with SAS URLs |
| Voice selection | ✅ Working | 16+ neural voices |
| Style selection | ✅ Working | Multiple expressive styles |
| **Intelligent File Naming** | ✅ **NEW** | Descriptive names from input text |
| iOS Shortcuts | ✅ Working | See setup guide |
| Web app | ✅ Working | Separate repo |

### Deployment Status
- **Function App**: Running
- **Speech Service**: Active
- **Blob Storage**: Available
- **Last Deploy**: December 17, 2025 - Intelligent file naming feature

## Known Issues

### Minor Issues
1. **Blob Cleanup**: Audio files not auto-deleted
   - Manual cleanup needed periodically
   - Low priority (storage is cheap)

2. **Style Compatibility**: Not all voices support all styles
   - `story_config.py` documents which styles each voice supports
   - API returns error if incompatible

3. **Timeout Edge Cases**: Very long texts (>30 min) may timeout
   - 3 min polling limit in `batch-check`
   - Workaround: Call `batch-check` again

### No Critical Issues
No blocking issues in production.

## Evolution of Project Decisions

### Initial Approach → Current Approach

1. **Synchronous → Asynchronous**
   - Started with sync API (times out for long texts)
   - Moved to batch synthesis API for reliability

2. **Direct Response → Pre-signed URLs**
   - Originally returned audio in response
   - Changed to SAS URLs for iOS Shortcuts compatibility

3. **Client Polling → Internal Polling**
   - Originally client polled repeatedly
   - Now `batch-check` polls internally (simpler for Shortcuts)

4. **Hardcoded Config → Separated Config**
   - Voice/style settings were in main code
   - Moved to `story_config.py` for easy customization

5. **Generic UUIDs → Intelligent File Naming** ✨ NEW
   - Originally files named `story_uuid.mp3`
   - Now named descriptively: `hello-world-this-is-a-test_6bf47a18.mp3`
   - Implemented Option A (simple text extraction)
   - Option B (AI-powered) documented for future

## Milestones Achieved

- [x] Initial project setup
- [x] Basic TTS functionality
- [x] Batch synthesis for long texts
- [x] Pre-signed URL generation
- [x] Azure deployment
- [x] iOS Shortcuts integration
- [x] Web app frontend (separate repo)
- [x] Comprehensive documentation
- [x] Memory Bank initialization
- [x] **Intelligent file naming feature** (December 2025)
- [x] Code cleanup (removed unused files)
