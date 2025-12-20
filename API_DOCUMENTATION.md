# ToniSynthFunc API Documentation

## Overview

ToniSynthFunc is an Azure Functions-based Text-to-Speech API designed for generating audio files from text, with special support for bedtime stories featuring multiple character voices.

**Base URL:** `https://<your-function-app>.azurewebsites.net/api`

---

## Authentication

All endpoints require a function key passed via query parameter or header:

```
?code=<your-function-key>
```

Or header:
```
x-functions-key: <your-function-key>
```

---

## Endpoints

### POST /batch-start

Start an asynchronous batch synthesis job. Ideal for long texts (bedtime stories).

#### Request Body

```json
{
  "text": "string (required) - The text to synthesize",
  "voice": "string (optional) - Azure Neural Voice name (default: en-US-GuyNeural)",
  "style": "string (optional) - Speaking style (default: hopeful)",
  "enable_character_voices": "boolean (optional) - Enable multi-voice dialogue",
  "character_voices": "object (optional) - Custom voice mappings for characters"
}
```

#### Adventure Mode Auto-Detection

When `enable_character_voices` is not explicitly set, the API automatically enables character voices if the text appears to be a story/adventure based on:
- Keywords in first 10 words: "story", "adventure", "tale", "once"
- Opening patterns: "Once upon a time", "Long ago", "Chapter 1", "Prologue"

#### Markdown Formatting Support

The API automatically cleans markdown formatting from input text to produce natural-sounding speech:

**Handled automatically:**
- **Tables** - Completely removed (as requested per issue #1)
- **Bullets/Lists** - Converted to plain sentences (items read as normal lines)
- **Headers** (`# ## ###`) - Converted to plain text
- **Bold/Italic** (`**text**`, `*text*`) - Markers removed, text preserved
- **Links** (`[text](url)`) - URL removed, link text preserved
- **Code blocks** - Removed entirely
- **Horizontal rules** (`---`) - Removed
- **Blockquotes** (`>`) - Markers removed, text preserved

**Example:**
```markdown
# The Adventure

Here are the characters:
- **Alice** - The hero
- Bob - The sidekick

| Name | Role |
|------|------|
| Alice | Hero |

Once upon a time...
```

Becomes:
```text
The Adventure

Here are the characters:
Alice - The hero
Bob - The sidekick

Once upon a time...
```

The response includes a `markdown_cleaned` boolean indicating if any markdown was removed.

#### Response (200 OK)

```json
{
  "status": "started",
  "synthesis_id": "string - Unique job identifier",
  "audio_url": "string - Pre-signed URL (available when complete)",
  "status_check_url": "string - URL to check job status",
  "voice": "string - Voice used",
  "enable_character_voices": "boolean",
  "adventure_mode_auto_detected": "boolean",
  "markdown_cleaned": "boolean - True if markdown formatting was removed",
  "text_length": "number - Character count (after markdown cleaning)",
  "estimated_duration_minutes": "number",
  "message": "string"
}
```

#### Error Responses

- `400 Bad Request` - Invalid input (missing text, invalid voice, etc.)
- `500 Internal Server Error` - Azure Speech Service error

---

### GET /batch-check

Check the status of a synthesis job and retrieve the audio URL when complete.

**Note:** This endpoint polls internally for up to 3 minutes before returning.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| synthesis_id | string | Yes | The synthesis job ID from batch-start |

#### Response - Completed (200 OK)

```json
{
  "status": "completed",
  "synthesis_id": "string",
  "audio_url": "string - SAS URL valid for 48 hours",
  "size_bytes": "number",
  "duration_seconds": "number",
  "message": "string"
}
```

#### Response - Still Processing (200 OK with status)

```json
{
  "status": "processing",
  "synthesis_id": "string",
  "message": "string"
}
```

#### Response - Timeout (408 Request Timeout)

```json
{
  "status": "timeout",
  "synthesis_id": "string",
  "message": "string",
  "elapsed_seconds": "number"
}
```

#### Error Responses

- `400 Bad Request` - Missing synthesis_id
- `404 Not Found` - Synthesis job not found
- `500 Internal Server Error` - Failed to check status

---

### POST /sync-tts

Synchronous text-to-speech synthesis. Limited to ~5000 characters.

**Use batch-start for longer texts (bedtime stories).**

#### Request Body

```json
{
  "text": "string (required) - Max 5000 characters",
  "voice": "string (optional) - Azure Neural Voice name",
  "style": "string (optional) - Speaking style",
  "enable_character_voices": "boolean (optional)"
}
```

#### Response (200 OK)

```json
{
  "status": "success",
  "url": "string - SAS URL for audio file",
  "filename": "string",
  "voice": "string",
  "size_bytes": "number",
  "text_length": "number"
}
```

#### Error Responses

- `400 Bad Request` - Text too long (>5000 chars) or missing

---

## Available Voices

### Primary Story Voices

| Voice | Gender | Best For |
|-------|--------|----------|
| en-US-GuyNeural | Male | Bible stories, narration |
| en-US-AriaNeural | Female | Expressive stories |
| en-US-JennyNeural | Female | Bedtime, calm stories |
| en-US-DavisNeural | Male | Adventure stories |
| en-US-SaraNeural | Female | Cheerful content |

### Speaking Styles

Available styles vary by voice. Common styles include:

- `friendly` - Warm, approachable
- `hopeful` - Positive, uplifting
- `cheerful` - Happy, energetic
- `excited` - Enthusiastic
- `sad` - Somber, emotional
- `angry` - Intense
- `whispering` - Quiet, intimate
- `shouting` - Loud, urgent
- `terrified` - Scared

---

## Character Voices

When `enable_character_voices` is true, the API:

1. **Detects dialogue** using quote patterns
2. **Identifies characters** from attribution (e.g., "said Mary")
3. **Assigns voices** based on detected/inferred gender
4. **Applies expressions** based on speech verbs (whispered, shouted, etc.)

### Custom Character Mappings

Override automatic detection with custom mappings:

```json
{
  "text": "...",
  "enable_character_voices": true,
  "character_voices": {
    "narrator": {
      "voice": "en-US-GuyNeural",
      "style": "friendly"
    },
    "princess": {
      "voice": "en-US-JennyNeural",
      "style": "cheerful",
      "gender": "female"
    },
    "dragon": {
      "voice": "en-US-DavisNeural",
      "style": "angry",
      "gender": "male"
    }
  }
}
```

---

## Story Presets

Pre-configured voice settings for different story types:

| Preset | Voice | Style | Description |
|--------|-------|-------|-------------|
| bedtime | en-US-JennyNeural | (default) | Calm, soothing |
| adventure | en-US-DavisNeural | excited | Action-packed |
| gentle | en-US-AriaNeural | friendly | Soft, warm |
| cheerful | en-US-SaraNeural | cheerful | Happy, upbeat |

---

## Rate Limits

- **Batch synthesis:** 20 concurrent jobs per subscription
- **Sync TTS:** Limited by Azure Speech Service quotas
- **Audio file retention:** 24-48 hours

---

## iOS Shortcuts Integration

See [iOS_SHORTCUTS_GUIDE.md](iOS_SHORTCUTS_GUIDE.md) for integration instructions.

### Quick Setup

1. Call `/batch-start` with your story text
2. Save the `synthesis_id` and `audio_url`
3. Call `/batch-check?synthesis_id=<id>` to wait for completion
4. Download audio from the returned URL

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid input data |
| TEXT_TOO_LONG | 400 | Text exceeds maximum length |
| SYNTHESIS_NOT_FOUND | 404 | Job ID not found |
| SYNTHESIS_FAILED | 500 | Azure Speech Service error |
| SYNTHESIS_TIMEOUT | 408 | Job took too long |
| CONFIGURATION_ERROR | 500 | Missing environment config |
| STORAGE_ERROR | 500 | Blob storage operation failed |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |

---

## Examples

### Simple Story Synthesis

```bash
curl -X POST "https://your-app.azurewebsites.net/api/batch-start?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Once upon a time, there was a brave little dragon named Spark.",
    "voice": "en-US-GuyNeural",
    "style": "friendly"
  }'
```

### Check Job Status

```bash
curl "https://your-app.azurewebsites.net/api/batch-check?code=YOUR_KEY&synthesis_id=once-upon-a-time-12345678"
```

### Multi-Voice Story

```bash
curl -X POST "https://your-app.azurewebsites.net/api/batch-start?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "\"Hello!\" said Princess Luna. \"Greetings,\" replied the dragon.",
    "enable_character_voices": true
  }'
```
