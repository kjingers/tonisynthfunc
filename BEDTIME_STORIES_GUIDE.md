# Bedtime Stories TTS - Azure Setup Guide

## 🎯 Solution Overview

Your Azure Function App now has **3 endpoints** for text-to-speech synthesis:

### 1. `/api/start-synthesis` ⭐ RECOMMENDED FOR BEDTIME STORIES
**Async batch synthesis - perfect for 20-30 minute stories!**

- **Returns immediately** (~1-2 seconds)
- Supports unlimited text length (even 1+ hour audio)
- Returns a pre-signed URL that will work once synthesis completes
- Similar to your AWS Polly async workflow

### 2. `/api/check-synthesis`
**Check if synthesis is complete and get the download URL**

- Checks batch synthesis status
- Downloads audio from Azure and uploads to your blob storage
- Returns the final audio URL when ready

### 3. `/api/tonieboxsynthesize` (LEGACY)
**Synchronous - only for short texts (<5000 chars)**

- Returns audio immediately, but times out for long texts
- Max ~10 minutes of audio

---

## 📱 iOS Shortcut Workflow (Same as AWS!)

### Shortcut #1: Start Story Synthesis

```
Text from Clipboard → Copy to variable "storyText"

Get contents of URL:
  URL: https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/start-synthesis?code=YOUR_FUNCTION_KEY
  Method: POST
  Headers: Content-Type: application/json
  Request Body: JSON
    {
      "text": [storyText],
      "voice": "en-US-GuyNeural"
    }

Get dictionary value for "audio_url" from response
Copy to Clipboard

Show notification: "Story synthesis started! Check back in 2-3 minutes."
```

### Shortcut #2: Check & Download Story

```
URL from Clipboard → Copy to variable "audioURL"

Get contents of URL: [audioURL]

If response size > 1000 bytes:
  → Save file (story is ready!)
  → Show notification: "Story downloaded!"
Else:
  → Show notification: "Story not ready yet. Try again in 60 seconds."
```

---

## 🔑 Get Your Function Keys

Run these commands to get your function keys:

```powershell
# Start-synthesis key
az functionapp function keys list `
  --function-name start-synthesis `
  --name tonisynthfunc `
  --resource-group toni-stories-vis

# Check-synthesis key
az functionapp function keys list `
  --function-name check-synthesis `
  --name tonisynthfunc `
  --resource-group toni-stories-vis
```

---

## 🧪 Testing Your Functions

### Test 1: Start a Synthesis

```powershell
$key = "YOUR_FUNCTION_KEY"
$url = "https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/start-synthesis?code=$key"

$body = @{
    text = "Once upon a time, in a land far away, there lived a brave little dragon who loved to read bedtime stories to all the forest animals. Every night, the dragon would gather the rabbits, foxes, and bears around a cozy campfire..."
    voice = "en-US-GuyNeural"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 10

# Save the synthesis_id and audio_url
$synthesisId = $response.synthesis_id
$audioUrl = $response.audio_url
```

### Test 2: Check Synthesis Status

```powershell
$checkKey = "YOUR_CHECK_FUNCTION_KEY"
$checkUrl = "https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/check-synthesis?synthesis_id=$synthesisId&code=$checkKey"

# Wait 60 seconds, then check status
Start-Sleep -Seconds 60
$status = Invoke-RestMethod -Uri $checkUrl -Method Get
$status | ConvertTo-Json -Depth 10

# If status="completed", download the audio
if ($status.status -eq "completed") {
    Invoke-WebRequest -Uri $audioUrl -OutFile "bedtime-story.mp3"
    Write-Host "Story downloaded! File size: $((Get-Item bedtime-story.mp3).Length) bytes"
}
```

---

## ⚙️ How It Works (Under the Hood)

### Start-Synthesis Flow:
1. Receives text from iPhone
2. Creates a batch synthesis job with Azure Speech Service (NEW Batch Synthesis API)
3. Generates a pre-signed blob storage URL (like AWS S3 pre-signed URL)
4. Returns immediately with:
   - `synthesis_id` - track the job
   - `audio_url` - pre-signed URL (works once synthesis completes)
   - `status_check_url` - URL to check progress

### Check-Synthesis Flow:
1. Queries Azure batch synthesis status
2. If still processing → returns "processing" status
3. If complete → Downloads ZIP from Azure → Extracts MP3 → Uploads to your blob storage
4. Returns the download URL

### Why This Works for 20-30 Min Stories:
- **Batch Synthesis API** is designed for long audio (books, lectures, etc.)
- No timeout issues (async processing)
- Typically completes in 1-3 minutes regardless of audio length
- Much faster than AWS Polly for long texts!

---

## 🎙️ Available Voices

Popular voices for bedtime stories:

**Male voices:**
- `en-US-GuyNeural` (default) - friendly, warm
- `en-US-EricNeural` - expressive storyteller
- `en-GB-RyanNeural` - British accent

**Female voices:**
- `en-US-JennyNeural` - warm, conversational
- `en-US-AriaNeural` - expressive, friendly
- `en-GB-SoniaNeural` - British accent

**Child-friendly:**
- `en-US-AnaNeural` - young, cheerful
- `en-US-MonicaNeural` - clear, gentle

Full list: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts

---

## 📊 Pricing Estimate

For bedtime stories (20-30 min audio):

**Speech Service (Neural TTS):**
- $16 per 1 million characters
- 30-min story ≈ 15,000 characters
- Cost: **$0.24 per story**

**Blob Storage:**
- Storage: $0.018 per GB/month
- 30-min MP3 ≈ 30 MB
- Egress (download): $0.087 per GB
- Cost: **~$0.003 per story**

**Function App (Consumption Plan):**
- First 1M executions free
- $0.20 per million executions after
- Cost: **virtually free**

**Total: ~$0.25 per bedtime story** 💰

Compare to AWS Polly: ~$0.40-0.60 per story (neural voices)

---

## 🔧 Configuration Details

### Your Resources:
- **Function App:** tonisynthfunc
- **Speech Service:** toniebox-speech-service (eastus)
- **Storage Account:** tonistoriesvisa86b (westus3)
- **Container:** audiofilestoni
- **Resource Group:** toni-stories-vis

### Environment Variables (Already Configured):
```
SPEECH_SERVICE_KEY=<YOUR_SPEECH_SERVICE_KEY>
SPEECH_SERVICE_REGION=eastus
STORAGE_ACCOUNT_NAME=tonistoriesvisa86b
STORAGE_ACCOUNT_KEY=<YOUR_STORAGE_ACCOUNT_KEY>
STORAGE_CONTAINER_NAME=audiofilestoni
```

---

## 🚀 Next Steps

1. **Get your function keys** (see commands above)
2. **Create iOS Shortcuts** using the workflow above
3. **Test with a sample story** (see testing section)
4. **Enjoy automated bedtime stories!** 🌙

---

## 🔍 Troubleshooting

### "Synthesis timeout" error:
- This shouldn't happen with batch synthesis
- Typical synthesis time: 1-3 minutes for any length

### "No audio file found in results":
- Check Azure Portal → Speech Service → Batch Synthesis jobs
- Verify the synthesis completed successfully

### Pre-signed URL returns XML error:
- File not uploaded yet (synthesis still processing)
- Wait and call `/api/check-synthesis` to trigger upload

### Function returns 500 error:
- Check Function App logs in Azure Portal
- Verify environment variables are set correctly

---

## 📝 API Reference

### POST /api/start-synthesis

**Request:**
```json
{
  "text": "Your story text here...",
  "voice": "en-US-GuyNeural"  // optional
}
```

**Response:**
```json
{
  "status": "started",
  "synthesis_id": "story-abc123...",
  "audio_url": "https://...blob.core.windows.net/...?sas_token",
  "status_check_url": "https://.../api/check-synthesis?synthesis_id=...",
  "voice": "en-US-GuyNeural",
  "text_length": 15000,
  "estimated_duration_minutes": 7.5,
  "message": "Synthesis started. Audio URL will be available when complete..."
}
```

### GET /api/check-synthesis?synthesis_id=XXX

**Response (Processing):**
```json
{
  "status": "processing",
  "synthesis_id": "story-abc123...",
  "message": "Synthesis in progress. Check again in 30-60 seconds."
}
```

**Response (Completed):**
```json
{
  "status": "completed",
  "synthesis_id": "story-abc123...",
  "audio_url": "https://...blob.core.windows.net/...?sas_token",
  "size_bytes": 5242880,
  "duration_seconds": 1800,
  "message": "Synthesis complete. Audio ready for download."
}
```

---

**Happy storytelling! 📖✨**

