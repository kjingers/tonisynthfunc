# Product Context - Toni TTS

## Why This Project Exists

### Problem Statement
Parents want to create personalized bedtime stories for their children with natural-sounding narration. Existing TTS solutions either:
- Have length limits (can't handle 20-30 minute stories)
- Lack expressive speaking styles
- Require complex setup
- Are expensive for personal use

### Solution
Toni TTS provides a simple API that:
1. Accepts any length of text
2. Converts it to high-quality speech with Azure's neural voices
3. Returns a download link for the audio file
4. Supports expressive styles perfect for storytelling

## How It Should Work

### User Flow (iOS Shortcut - Primary Use Case)
1. User triggers iOS Shortcut with story text
2. Shortcut calls `batch-start` endpoint
3. Shortcut calls `batch-check` with polling
4. Audio URL is returned when ready
5. User can play/download the audio

### User Flow (Web App)
1. User pastes story text in web interface
2. Selects voice and style
3. Clicks "Generate"
4. Progress indicator shows synthesis status
5. Audio plays in browser when ready

## User Experience Goals

### Primary UX Goals
- **Simplicity**: One-click generation from iOS Shortcuts
- **Speed**: Audio ready within 1-3 minutes
- **Quality**: Natural, expressive narration
- **Reliability**: Works consistently for long texts

### Voice & Style Experience
- Default voice: `en-US-GuyNeural` (male, warm, good for narration)
- Default style: `hopeful` (positive, faith-filled tone)
- Multiple style options for different story moods

## Target Personas

### Primary: Parent with Toddlers
- Creates personalized bedtime stories
- Uses iOS Shortcuts for hands-free operation
- Wants warm, soothing narration
- Stories typically 15-30 minutes

### Secondary: Bible Story Narrator
- Converts Bible passages to audio
- Prefers "hopeful" speaking style
- May use web app for longer sessions

## Key Differentiators

1. **Long-form support**: Unlike basic TTS APIs, supports 30+ minute audio
2. **Async processing**: Doesn't timeout on long texts
3. **Pre-signed URLs**: Secure, shareable download links
4. **iOS Shortcuts friendly**: Designed for Apple ecosystem integration
5. **Low cost**: ~$1-5/month for personal use
