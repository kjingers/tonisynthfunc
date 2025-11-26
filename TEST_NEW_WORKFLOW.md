# Testing New iOS-Friendly Workflow

## ✅ WHAT CHANGED

**OLD (Complicated for iOS)**:
1. Call `batch-start` → Get synthesis_id
2. Call `batch-check` → Returns "processing, try again in 60s"
3. Wait 60s in iOS Shortcut (complicated)
4. Call `batch-check` again → Returns "processing, try again in 60s"
5. Repeat until complete...

**NEW (Simple - Like AWS Lambda)**:
1. Call `batch-start` → Get synthesis_id and SAS URL
2. Call `batch-check?synthesis_id=xxx` → **Waits internally for up to 3 minutes**, returns URL when ready
3. Download MP3 from URL

## ⚡ Test Commands

### Step 1: Start Synthesis

```powershell
$key = "<YOUR_FUNCTION_KEY>"
$url = "https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-start?code=$key"

$body = @{
    text = "Once upon a time, there was a brave little dragon named Spark who loved bedtime stories. Every night, Spark would fly through the starry sky, collecting dreams from the clouds and sharing them with children around the world. Tonight's dream was about a magical forest where trees sang lullabies and flowers glowed in the moonlight."
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 10

# Save the synthesis_id
$synthesisId = $response.synthesis_id
Write-Host "Synthesis ID: $synthesisId" -ForegroundColor Green
```

### Step 2: Check & Download (NOW WAITS INTERNALLY!)

```powershell
# This will wait up to 3 minutes for synthesis to complete
$checkUrl = "https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-check?synthesis_id=$synthesisId&code=$key"

Write-Host "Checking status (this will wait up to 3 minutes)..." -ForegroundColor Yellow
$result = Invoke-RestMethod -Uri $checkUrl -Method Get
$result | ConvertTo-Json -Depth 10

# Download the MP3
if ($result.status -eq "completed") {
    $audioUrl = $result.audio_url
    Invoke-WebRequest -Uri $audioUrl -OutFile "bedtime-story.mp3"
    Write-Host "✅ Story downloaded! File size: $((Get-Item bedtime-story.mp3).Length) bytes" -ForegroundColor Green
    Write-Host "Duration: $($result.duration_seconds) seconds" -ForegroundColor Cyan
}
```

## 📱 iOS Shortcuts (NOW SIMPLE!)

### Shortcut 1: Start Bedtime Story

```
Get text from: Clipboard
Set variable: storyText

URL: https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-start?code=<YOUR_FUNCTION_KEY>
Method: POST
Headers:
  Content-Type: application/json
Body:
{
  "text": [storyText]
}

Get: synthesis_id from response
Set variable: synthesisID

Copy to Clipboard: [synthesisID]
Show Notification: "Story started! Run 'Download Story' shortcut in 2-3 minutes"
```

### Shortcut 2: Download Story (SIMPLIFIED!)

```
Get text from: Clipboard
Set variable: synthesisID

URL: https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api/batch-check?synthesis_id=[synthesisID]&code=<YOUR_FUNCTION_KEY>
Method: GET

Wait for response (will take 10s-3min)

Get: audio_url from response
Set variable: audioURL

Download file from: [audioURL]
Save to: Files/Bedtime Stories/
Show Notification: "Story ready!"
```

**That's it! No loops, no retries, no complex logic!**

## 🎯 How It Works Now

`batch-check` endpoint now:
1. Polls Azure Speech Service every 10 seconds
2. Waits up to 3 minutes (18 attempts)
3. When "Succeeded", downloads ZIP, extracts MP3, uploads to blob
4. Returns the final SAS URL to download

iOS Shortcut just calls it once and waits for the response!

## ⏱️ Timeout Behavior

- If synthesis takes longer than 3 minutes (rare), returns 408 timeout
- iOS Shortcut can just retry by calling `batch-check` again
- Much simpler than managing polling logic in iOS Shortcuts

## 💡 Benefits

✅ iOS Shortcuts are now as simple as AWS Lambda workflow
✅ No complex retry logic needed in iOS
✅ Function handles all the waiting and polling
✅ Matches your existing AWS Polly mental model
✅ Same two-shortcut pattern you're familiar with

