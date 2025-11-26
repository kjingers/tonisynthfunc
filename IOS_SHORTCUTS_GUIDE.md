# iOS Shortcuts Setup Guide - Azure Bedtime Stories

## 🎯 Overview

This guide will help you create two iOS Shortcuts to generate bedtime stories using your Azure Function App. The workflow is **nearly identical** to your AWS Lambda setup!

### How It Works:
1. **Shortcut 1**: Start synthesis → Returns synthesis_id
2. Wait 2-3 minutes
3. **Shortcut 2**: Check & download → Returns MP3 file

---

## 📱 Shortcut 1: Start Bedtime Story

### What This Does:
- Takes text from clipboard (your story)
- Sends to Azure Function to start synthesis
- Returns a synthesis_id
- Saves synthesis_id to clipboard for next shortcut

### Step-by-Step Instructions:

#### 1. Create New Shortcut
- Open **Shortcuts** app
- Tap **+** (top right)
- Name it: **"Start Bedtime Story"**

#### 2. Get Story Text
**Action**: `Get Clipboard`
- Search for "Get Clipboard"
- Add it (this gets your story text)

**Action**: `Set Variable`
- Search for "Set Variable"
- Name it: `storyText`

#### 3. Call Azure Function (Start Synthesis)

**Action**: `Get Contents of URL`
- Search for "Get Contents of URL"
- Configure:

**URL**:
```
https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-start?code=<YOUR_FUNCTION_KEY>
```

**Method**: `POST`

**Headers**: 
- Tap "Add new field" → Choose "Header"
- Key: `Content-Type`
- Value: `application/json`

**Request Body**: `JSON`
- Tap "Request Body" → Choose "JSON"
- Tap in the JSON field and build:

```json
{
  "text": [storyText]
}
```

*Note: Tap "storyText" to insert the variable from step 2*

**Show More** (expand options):
- **Get Type**: `JSON`

#### 4. Extract Synthesis ID

**Action**: `Get Dictionary Value`
- Search for "Get Dictionary Value"
- Get value for key: `synthesis_id`
- From: `Contents of URL`

**Action**: `Set Variable`
- Name it: `synthesisID`

#### 5. Save to Clipboard & Notify

**Action**: `Copy to Clipboard`
- Input: `synthesisID` variable

**Action**: `Show Notification`
- Title: `Story Started!`
- Body: `Run "Download Story" shortcut in 2-3 minutes`

**Action**: `Show Result`
- Input: `synthesisID`
- This displays the ID on screen

---

## 📥 Shortcut 2: Download Story

### What This Does:
- Gets synthesis_id from clipboard
- Calls Azure Function to check status (waits internally up to 3 minutes)
- Downloads MP3 file when ready
- Saves to Files or Music

### Step-by-Step Instructions:

#### 1. Create New Shortcut
- Open **Shortcuts** app
- Tap **+** (top right)
- Name it: **"Download Story"**

#### 2. Get Synthesis ID

**Action**: `Get Clipboard`
- This gets the synthesis_id from Shortcut 1

**Action**: `Set Variable`
- Name it: `synthesisID`

#### 3. Call Azure Function (Check & Wait for Completion)

**Action**: `Get Contents of URL`
- Search for "Get Contents of URL"
- Configure:

**URL**:
```
https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-check?synthesis_id=[synthesisID]&code=<YOUR_FUNCTION_KEY>
```

*Note: Insert the `synthesisID` variable where `[synthesisID]` is shown*

**Method**: `GET`

**Show More**:
- **Get Type**: `JSON`

> ⏱️ **Important**: This call will wait up to 3 minutes for synthesis to complete. Your shortcut will appear to be "running" - this is normal!

#### 4. Extract Download URL

**Action**: `Get Dictionary Value`
- Get value for key: `audio_url`
- From: `Contents of URL`

**Action**: `Set Variable`
- Name it: `audioURL`

#### 5. Download MP3 File

**Action**: `Get Contents of URL`
- URL: `audioURL` (the variable)
- Method: `GET`

#### 6. Save File

**Option A: Save to Files App**

**Action**: `Save File`
- File: `Contents of URL` (from step 5)
- Ask Where to Save: `On` (or choose specific folder)
- Suggested path: `iCloud Drive/Bedtime Stories/`
- Overwrite if File Exists: `On` (optional)

**Option B: Save to Music/Voice Memos**

**Action**: `Save to Photo Album`
*(iOS will detect it's audio and save to appropriate app)*

#### 7. Notify Success

**Action**: `Show Notification`
- Title: `Story Ready!`
- Body: `Bedtime story downloaded successfully`

**Action**: `Show Result`
- Input: `audioURL`

---

## 🔄 Comparison with Your AWS Lambda Shortcuts

### Similarities (What Stays the Same):
✅ Same two-shortcut pattern
✅ Shortcut 1: Start synthesis, save ID
✅ Shortcut 2: Check status and download
✅ Uses clipboard to pass synthesis_id between shortcuts
✅ JSON request/response format

### Differences (What Changed):

| AWS Lambda | Azure Functions |
|------------|-----------------|
| Lambda function URL | Azure Function App URL with `?code=` parameter |
| Returns pre-signed S3 URL | Returns pre-signed SAS URL (blob storage) |
| May need immediate download | **Wait happens in Azure Function** (easier!) |
| IAM authentication | Function key in URL |
| `lambda.us-east-1.amazonaws.com` | `azurewebsites.net` |

### Key Improvement: 🎉
**Your AWS shortcut probably had retry logic or manual waiting.** 

**Azure version is simpler!** The `batch-check` endpoint **waits internally** for up to 3 minutes, so your iOS Shortcut just calls it once and waits for the response. No loops, no retries!

---

## 🧪 Testing Your Shortcuts

### Test Shortcut 1:
1. Copy this text to clipboard:
```
Once upon a time, there was a brave little dragon named Spark who loved bedtime stories. Every night, Spark would fly through the starry sky, collecting dreams from the clouds and sharing them with children around the world.
```

2. Run **"Start Bedtime Story"** shortcut
3. You should see a synthesis ID like: `story-a8965571-e254-4c75-8ef0-d7d691990073`
4. ID is automatically copied to clipboard

### Test Shortcut 2:
1. Wait 2-3 minutes (get a snack! ☕)
2. Run **"Download Story"** shortcut
3. Shortcut will wait (10 seconds to 3 minutes) 
4. MP3 file downloads automatically
5. Save location: Choose where to save

---

## 💡 Tips & Best Practices

### Timing:
- Short stories (< 500 words): Wait **1 minute** before downloading
- Medium stories (500-2000 words): Wait **2 minutes**
- Long stories (2000+ words): Wait **3 minutes**

### Storage:
- Create a dedicated folder: `iCloud Drive/Bedtime Stories/`
- Organize by date or child's name
- Delete old stories to save space

### Error Handling:
If **Download Story** shortcut fails:
- Check internet connection
- Wait another minute and try again
- Synthesis_id is still in clipboard
- Can retry unlimited times (48-hour expiration)

### Voice Selection (Optional):
To use a different voice, modify Shortcut 1's JSON:

```json
{
  "text": [storyText],
  "voice": "en-US-AriaNeural",
  "style": "cheerful"
}
```

**Popular voices**:
- `en-US-JennyNeural` (default, warm female)
- `en-US-AriaNeural` (expressive female)
- `en-US-GuyNeural` (friendly male)
- `en-US-DavisNeural` (deep male)

**Styles** (optional):
- `cheerful` - Happy, upbeat
- `gentle` - Soft, soothing (great for bedtime!)
- `excited` - Enthusiastic
- `sad` - Emotional stories

---

## 🐛 Troubleshooting

### "Invalid URL" error:
- Make sure you inserted the `synthesisID` variable correctly
- Don't type `[synthesisID]` literally - use the variable picker

### "Request timed out":
- Normal! Synthesis can take 1-3 minutes
- Shortcut should wait automatically
- If it truly times out after 3 minutes, just run **Download Story** again

### "No audio_url in response":
- Synthesis may have failed
- Check the response JSON for error message
- Try running **Start Bedtime Story** again with different text

### "Could not download file":
- SAS URL might have expired (rare within 48 hours)
- Run **Start Bedtime Story** again to get fresh URL

---

## 🎨 Customization Ideas

### Add Text Input:
Instead of clipboard, add **"Ask for Input"** action at start of Shortcut 1

### Quick Actions:
Add shortcuts to home screen:
- Settings → Shortcuts → Your shortcut → Add to Home Screen

### Siri Integration:
Say: *"Hey Siri, start bedtime story"*
(Shortcuts automatically work with Siri)

### Multiple Voices:
Create separate shortcuts for different narrators:
- "Start Story (Jenny)"
- "Start Story (Guy)"
- "Start Story (Cheerful Aria)"

---

## 📋 Quick Reference

### Shortcut 1 Summary:
```
Get Clipboard → Set Variable (storyText)
→ POST to batch-start endpoint with JSON body
→ Extract synthesis_id → Copy to Clipboard
→ Show notification
```

### Shortcut 2 Summary:
```
Get Clipboard (synthesisID)
→ GET batch-check endpoint (waits internally)
→ Extract audio_url
→ Download MP3
→ Save file
→ Show notification
```

### Function Keys:
```
Host Key: <YOUR_FUNCTION_KEY>
```

### Endpoints:
```
Start: https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-start?code={KEY}

Check: https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-check?synthesis_id={ID}&code={KEY}
```

---

## 🎉 You're Done!

Your shortcuts should now work exactly like your AWS Lambda setup, but with **simpler polling logic** since Azure handles the waiting for you!

**Questions?** Check the logs in Azure Portal → Function App → Monitor

