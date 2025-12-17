# System Patterns - Toni TTS

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Options                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Web App       │   Expo iOS App  │   iOS Shortcuts             │
│   (React)       │   (React Native)│   (Native Apple)            │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                       │
         └─────────────────┼───────────────────────┘
                           ▼
              ┌────────────────────────┐
              │   Azure Functions      │
              │   (This Repo)          │
              │                        │
              │  • /api/batch-start    │
              │  • /api/batch-check    │
              │  • /api/sync-tts       │
              └───────────┬────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│ Azure Cognitive │ │ Azure Blob   │ │ Azure Batch  │
│ Services Speech │ │ Storage      │ │ Synthesis    │
└─────────────────┘ └──────────────┘ └──────────────┘
```

## Key Technical Decisions

### 1. Async Batch Processing Pattern
**Decision**: Use Azure Batch Synthesis API for long texts instead of synchronous REST API.

**Rationale**:
- Synchronous API times out for texts >10 minutes of audio
- Batch API handles unlimited length
- Returns immediately, poll for completion

**Implementation**:
- `batch-start`: Creates batch synthesis job, returns synthesis_id
- `batch-check`: Polls Azure API with internal retry (up to 3 minutes)

### 2. Pre-signed URL Pattern
**Decision**: Generate SAS URLs for blob storage access instead of streaming audio directly.

**Rationale**:
- Reduces function execution time
- Works with iOS Shortcuts (direct download)
- Shareable, time-limited links

**Implementation**:
```python
sas_token = generate_blob_sas(
    account_name=...,
    container_name=...,
    blob_name=audio_filename,
    account_key=...,
    permission=BlobSasPermissions(read=True),
    expiry=datetime.utcnow() + timedelta(hours=SAS_URL_EXPIRY_HOURS)
)
```

### 3. SSML for Voice Styling
**Decision**: Use SSML (Speech Synthesis Markup Language) for voice and style control.

**Rationale**:
- Standard format supported by Azure
- Enables expressive speaking styles
- Future extensibility (prosody, emphasis, etc.)

**Implementation**:
```xml
<speak version='1.0' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>
    <voice name='{voice_name}'>
        <mstts:express-as style='{style}'>
            {text}
        </mstts:express-as>
    </voice>
</speak>
```

### 4. Configuration Separation
**Decision**: Separate voice/style configuration into `story_config.py`.

**Rationale**:
- Easy customization without modifying main code
- Documented voice/style combinations
- Preset configurations for different story types

## Design Patterns in Use

### Request-Response Pattern (Async)
1. Client sends text → receives synthesis_id
2. Client polls status → receives audio URL
3. Client downloads audio from blob storage

### Polling with Internal Retry
`batch-check` implements internal polling to simplify client:
- Polls up to 18 times (10 second intervals = 3 minutes max)
- Returns immediately when complete
- iOS Shortcuts only need one call (waits for response)

### Environment-Based Configuration
All secrets and configuration via environment variables:
- `SPEECH_SERVICE_KEY` - Azure Speech API key
- `SPEECH_SERVICE_REGION` - Azure region
- `STORAGE_ACCOUNT_NAME` - Blob storage account
- `STORAGE_ACCOUNT_KEY` - Blob storage key
- `STORAGE_CONTAINER_NAME` - Container for audio files

## Component Relationships

### function_app.py
Main Azure Functions module containing:
- `batch_start()` - Start synthesis job
- `batch_check()` - Check status, upload completed audio
- `sync_tts()` - Legacy synchronous endpoint

### story_config.py
Configuration module containing:
- Default voice/style settings
- Voice capabilities (which styles each voice supports)
- Story presets (bedtime, adventure, gentle, cheerful)
- Audio format configuration

## Critical Implementation Paths

### Batch Synthesis Flow
1. `batch-start` receives text
2. Generates unique synthesis_id
3. Creates SSML with voice/style
4. Calls Azure Batch Synthesis API (PUT)
5. Generates pre-signed SAS URL for future audio
6. Returns synthesis_id and SAS URL to client

### Status Check Flow
1. `batch-check` receives synthesis_id
2. Polls Azure Batch API for status
3. When "Succeeded":
   - Downloads ZIP result
   - Extracts MP3 audio
   - Uploads to Blob Storage
   - Returns audio URL
4. When timeout: Returns 408 status

## Error Handling Patterns

### Graceful Degradation
- Text >5000 chars: Redirect to batch API
- Synthesis timeout: Return 408 with retry suggestion
- API errors: Return detailed error info for debugging

### Logging
- Route hits logged for debugging
- Synthesis progress logged
- Errors logged with stack trace (`exc_info=True`)
