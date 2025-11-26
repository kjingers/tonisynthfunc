# iOS Shortcuts Setup Guide - Azure Bedtime Stories

## Your Azure Function Details

- **Function URL**: `https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net`
- **Function Key**: `<YOUR_FUNCTION_KEY>`
- **Container**: `audiofilestoni`

---

## Option 1: Simple One-Step Shortcut (Recommended)

This shortcut creates the story and automatically downloads it after waiting 2 minutes.

### Steps to Create:

1. **Open Shortcuts app** on your iPhone
2. **Tap "+"** to create new shortcut
3. **Name it**: "Bedtime Story"

### Add These Actions (in order):

#### Action 1: Get text input
- Search for **"Ask for Input"**
- Set prompt: `"Enter bedtime story text"`
- Input Type: **Text**
- Allow Multiple Lines: **ON**

#### Action 2: Set voice variable
- Search for **"Text"**
- Type: `en-US-JennyNeural`
- Tap the text → **Rename** → `Voice`

#### Action 3: Create JSON body
- Search for **"Dictionary"**
- Add two keys:
  - Key: `text` → Value: **Ask for Input** (from step 1)
  - Key: `voice` → Value: **Voice** (from step 2)

#### Action 4: Start synthesis
- Search for **"Get Contents of URL"**
- URL: `https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-start?code=<YOUR_FUNCTION_KEY>`
- Method: **POST**
- Headers:
  - `Content-Type`: `application/json`
- Request Body: **Dictionary** (from step 3)
- Tap "Show More" → Set **Request Body** to **JSON**

#### Action 5: Get synthesis ID from response
- Search for **"Get Dictionary Value"**
- Get: `synthesis_id`
- From: **Contents of URL** (from step 4)

#### Action 6: Show notification
- Search for **"Show Notification"**
- Text: `Story started! Waiting 2 minutes for synthesis...`

#### Action 7: Wait for synthesis
- Search for **"Wait"**
- Time: **120 seconds** (2 minutes)

#### Action 8: Check synthesis status
- Search for **"Get Contents of URL"**
- URL: `https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-check?code=<YOUR_FUNCTION_KEY>&synthesis_id=`
- After the `=`, tap the end and add **Dictionary Value** (synthesis_id from step 5)
- Method: **GET**

#### Action 9: Get audio URL from response
- Search for **"Get Dictionary Value"**
- Get: `audio_url`
- From: **Contents of URL** (from step 8)

#### Action 10: Download MP3
- Search for **"Get Contents of URL"**
- URL: **Dictionary Value** (audio_url from step 9)
- Method: **GET**

#### Action 11: Save to Files
- Search for **"Save File"**
- File: **Contents of URL** (from step 10)
- Ask Where to Save: **ON**
- (Or set a specific path like `iCloud Drive/Bedtime Stories/`)

#### Action 12: Success notification
- Search for **"Show Notification"**
- Text: `Bedtime story ready! 🌙`

---

## Option 2: Two-Step Shortcuts (More Flexible)

### Shortcut A: "Start Story"

1. Open Shortcuts → **New Shortcut**
2. Name: **"Start Story"**

**Actions:**

1. **Ask for Input** → `"Enter bedtime story text"` (Text, Multi-line ON)
2. **Text** → `en-US-JennyNeural` (rename to `Voice`)
3. **Dictionary**:
   - `text`: Ask for Input
   - `voice`: Voice
4. **Get Contents of URL**:
   - URL: `https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-start?code=<YOUR_FUNCTION_KEY>`
   - Method: POST
   - Headers: `Content-Type`: `application/json`
   - Body: Dictionary (as JSON)
5. **Get Dictionary Value** → `synthesis_id` from response
6. **Copy to Clipboard** → Dictionary Value
7. **Show Notification** → `Story started! ID copied. Run "Download Story" in 2 minutes.`

### Shortcut B: "Download Story"

1. Open Shortcuts → **New Shortcut**
2. Name: **"Download Story"**

**Actions:**

1. **Get Clipboard**
2. **Get Contents of URL**:
   - URL: `https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-check?code=<YOUR_FUNCTION_KEY>&synthesis_id=`
   - Add **Clipboard** after `synthesis_id=`
   - Method: GET
3. **Get Dictionary Value** → `status` from response
4. **If** → `status` **is** `completed`:
   - **Get Dictionary Value** → `audio_url` from response
   - **Get Contents of URL** → audio_url (download MP3)
   - **Save File** → Ask Where to Save
   - **Show Notification** → `Story ready! 🌙`
5. **Otherwise**:
   - **Show Notification** → `Still processing. Try again in 30 seconds.`

---

## Voice Options

Change the `Voice` variable in step 2 to any of these:

**Great for Bedtime Stories:**
- `en-US-JennyNeural` - Warm, friendly female (recommended!)
- `en-US-AriaNeural` - Soft, soothing female
- `en-US-GuyNeural` - Calm, gentle male
- `en-US-SaraNeural` - Clear, expressive female

**For Different Characters:**
- `en-US-DavisNeural` - Energetic male (for adventure stories)
- `en-US-JaneNeural` - Professional female
- `en-GB-SoniaNeural` - British female
- `en-GB-RyanNeural` - British male

Full list: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts

---

## Troubleshooting

### "Blob not found" error
- **Normal!** This means synthesis hasn't finished yet. Wait 30-60 more seconds and run "Download Story" again.

### Shortcut returns error
- Check that you're connected to internet
- Verify the function key hasn't changed: `az functionapp keys list --name tonisynthfunc --resource-group toni-stories-vis`

### Audio quality issues
- Neural voices require internet connection
- Try different voices (Jenny and Aria are best for kids)

### Long stories (20-30 min)
- Wait **3-5 minutes** instead of 2 minutes (change step 7)
- Or use the two-step shortcut and manually check when ready

---

## AWS Polly vs Azure Differences

**AWS Lambda** (what you had):
- No authentication needed if using IAM roles
- Returns MP3 directly in response

**Azure Functions** (what you have now):
- **Requires function key** in URL: `?code=YOUR_KEY`
- **Async workflow**: Start → Wait → Download
- **Pre-signed URLs**: Like S3, but Azure Blob SAS tokens
- **Better for long audio**: Supports 30+ minute stories (AWS Polly has 10-min limit)

---

## Cost Estimate

With your **$150/month Azure credits**:
- **~$0.27 per 20-minute story**
- **~500 stories/month** before using all credits
- **Actual cost**: ~$8/month for typical family use (30 stories)

---

## Tips for Kids

1. **Create multiple shortcuts** with preset voices for different characters
2. **Use Siri**: "Hey Siri, Bedtime Story" (enable Siri for the shortcut)
3. **Save to Files**: Create a "Bedtime Stories" folder in iCloud Drive
4. **Offline playback**: Downloaded MP3s work without internet

---

## Example Story Text

```
Once upon a time, in a magical forest far away, there lived a wise old owl named Oliver. 

Oliver had lived in the forest for over a hundred years, and he knew every tree, every stream, and every creature that called the forest home.

One beautiful spring morning, a young rabbit named Ruby hopped up to Oliver's tree...

[Continue your story - up to 30 minutes of audio!]
```

---

## Quick Reference

**Start Story URL:**
```
https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-start?code=<YOUR_FUNCTION_KEY>
```

**Check Status URL:**
```
https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-check?code=<YOUR_FUNCTION_KEY>&synthesis_id=YOUR_ID
```

**Request Format:**
```json
{
  "text": "Your bedtime story text here...",
  "voice": "en-US-JennyNeural"
}
```

**Response Format (batch-start):**
```json
{
  "status": "started",
  "synthesis_id": "story-abc-123",
  "audio_url": "https://...blob.core.windows.net/.../story-abc-123.mp3?se=...",
  "estimated_duration_minutes": 1.6
}
```

**Response Format (batch-check when complete):**
```json
{
  "status": "completed",
  "audio_url": "https://...blob.core.windows.net/.../story-abc-123.mp3?se=...",
  "duration_seconds": 205.5,
  "size_bytes": 2467840
}
```

---

Enjoy your bedtime stories! 🌙📖✨

