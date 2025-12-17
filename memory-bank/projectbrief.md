# Project Brief - Toni TTS Azure Functions Backend

## Project Overview
Toni TTS is a serverless Text-to-Speech backend powered by Azure Functions and Azure Cognitive Services. It provides a REST API for converting text to natural-sounding speech using Azure's neural voices.

## Core Requirements

### Primary Goals
1. Convert text to speech using Azure Cognitive Services
2. Support long-form content (20-30 minute bedtime stories)
3. Provide async batch processing for large texts
4. Return pre-signed URLs for audio download
5. Support multiple neural voices and speaking styles

### API Endpoints
- `POST /api/batch-start` - Start async batch synthesis job
- `GET /api/batch-check` - Check status and get audio URL
- `POST /api/sync-tts` - Synchronous TTS for short texts (legacy)

### Target Users
- Parent wanting to create bedtime stories for children
- iOS Shortcuts integration for hands-free operation
- Web and mobile app clients

## Technical Requirements

### Platform
- Azure Functions v4 (Python 3.11+)
- Azure Cognitive Services Speech
- Azure Blob Storage

### Key Features
- Neural TTS with 16+ voices
- Expressive speaking styles (hopeful, cheerful, whispering, etc.)
- Batch synthesis for texts of any length
- Pre-signed URLs with configurable expiry
- Function-level authentication

## Success Criteria
- Support texts up to 30+ minutes of audio
- Return audio URLs within 3 minutes of request
- Provide secure, time-limited download links
- Maintain low operational cost (~$1-5/month personal use)

## Repository
- GitHub: https://github.com/kjingers/tonisynthfunc.git
- Live endpoint: https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api

## Related Projects
- Web App: [tonisynthfunc-web](https://github.com/kjingers/tonisynthfunc-web) (React)
- iOS App: Same repo (Expo/React Native)
- iOS Shortcuts: Native Apple Shortcuts integration
