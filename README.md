# Toni TTS - Azure Functions Backend

A serverless Text-to-Speech backend powered by Azure Functions and Azure Cognitive Services. This is the backend API for the [tonisynthfunc-web](https://github.com/kjingers/tonisynthfunc-web) frontend.

## 🎯 Overview

Toni TTS provides a REST API for converting text to natural-sounding speech using Azure's neural voices. It supports batch processing for large texts (like 30-minute bedtime stories) and returns pre-signed URLs for audio download.

## ✨ Features

- 🎙️ **Neural TTS**: Azure Cognitive Services Speech with 16+ neural voices
- 🎭 **Expressive Styles**: Support for speaking styles (hopeful, cheerful, whispering, etc.)
- 📚 **Large Text Support**: Batch synthesis for texts of any length
- ⚡ **Async Processing**: Start synthesis and poll for completion
- 🔗 **Pre-signed URLs**: Secure, time-limited download links
- 📱 **iOS Shortcuts**: Direct integration with Apple Shortcuts app

## 🏗️ Architecture

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

## 📡 API Endpoints

### POST `/api/batch-start`
Start an async batch synthesis job.

**Request:**
```json
{
  "text": "Your long text to convert to speech...",
  "voice": "en-US-GuyNeural",
  "style": "hopeful"
}
```

**Response:**
```json
{
  "synthesis_id": "story-abc123",
  "status": "started",
  "text_length": 15000,
  "estimated_duration_minutes": 2.5
}
```

### GET `/api/batch-check?synthesis_id=<id>`
Check synthesis status and get audio URL when complete.

**Response (complete):**
```json
{
  "status": "completed",
  "audio_url": "https://storage.blob.core.windows.net/...",
  "duration_seconds": 180,
  "size_bytes": 2880000
}
```

### POST `/api/sync-tts`
Synchronous TTS for short texts (returns audio directly).

## 🛠️ Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: Azure Functions v4
- **Speech**: Azure Cognitive Services Speech
- **Storage**: Azure Blob Storage
- **Hosting**: Azure Functions Consumption Plan
- **Testing**: pytest with >80% coverage
- **CI/CD**: GitHub Actions

## 📦 Project Structure

```
tonisynthfunc/
├── function_app.py          # Main Azure Functions HTTP endpoints
├── character_voices.py      # Dialogue parsing and voice assignment
├── validators.py            # Input validation functions
├── markdown_utils.py        # Markdown cleaning for TTS
├── filename_utils.py        # Filename generation utilities
├── story_config.py          # Voice/style configuration and presets
├── http_helpers.py          # HTTP response helpers
├── exceptions.py            # Custom exception classes
├── logging_config.py        # Structured logging utilities
├── azure_clients.py         # Azure service client creation
├── storage_cleanup.py       # Storage cleanup utilities
├── requirements.txt         # Python dependencies
├── host.json                # Azure Functions host config
├── local.settings.json      # Local dev settings (gitignored)
├── tests/                   # Unit tests (pytest)
│   ├── test_character_voices.py
│   ├── test_validators.py
│   ├── test_markdown_utils.py
│   └── ...
├── .github/
│   ├── workflows/ci-cd.yml  # CI/CD pipeline
│   ├── copilot-instructions.md  # GitHub Copilot context
│   ├── CODEOWNERS           # Code ownership
│   ├── dependabot.yml       # Dependency updates
│   └── ISSUE_TEMPLATE/      # Issue templates
├── API_DOCUMENTATION.md     # Full API reference
├── CONTRIBUTING.md          # Contribution guidelines
└── iOS_SHORTCUTS_SETUP.md   # iOS Shortcuts integration
```

## 🤖 GitHub Copilot Integration

This repository is optimized for GitHub Copilot agent mode:

- **`.github/copilot-instructions.md`** - Custom instructions for Copilot
- **Issue templates** - Optimized for Copilot coding agent
- **Clear code patterns** - Type hints, docstrings, and consistent structure
- **Comprehensive tests** - 200+ tests for validation

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 🚀 Deployment

The function app is deployed to Azure Functions. The live endpoint is:
```
https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api
```

## 📱 Client Applications

| Client | Repository | Description |
|--------|------------|-------------|
| **Web App** | [tonisynthfunc-web](https://github.com/kjingers/tonisynthfunc-web) | React web interface |
| **iOS App** | [tonisynthfunc-web](https://github.com/kjingers/tonisynthfunc-web) | Expo/React Native (in same repo) |
| **iOS Shortcuts** | See `iOS_SHORTCUTS_SETUP.md` | Native Apple Shortcuts integration |

## 💰 Cost Management

### Disable the Function App (Stop All Costs)

To completely stop the function and avoid charges:

1. **Azure Portal Method:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to **Function Apps** → `tonisynthfunc`
   - Click **Stop** in the top toolbar
   - This stops execution but keeps the app configured

2. **Azure CLI Method:**
   ```bash
   az functionapp stop --name tonisynthfunc --resource-group <your-resource-group>
   ```

3. **Delete Everything (Nuclear Option):**
   ```bash
   # Delete the function app
   az functionapp delete --name tonisynthfunc --resource-group <your-resource-group>
   
   # Delete associated resources
   az cognitiveservices account delete --name <speech-service-name> --resource-group <your-resource-group>
   az storage account delete --name <storage-account-name> --resource-group <your-resource-group>
   ```

### Cost Breakdown

| Service | Pricing | Notes |
|---------|---------|-------|
| **Azure Functions** | Free tier: 1M executions/month | Consumption plan |
| **Speech Service** | $16 per 1M characters | Neural voices |
| **Blob Storage** | ~$0.02/GB/month | Audio file storage |

**Typical monthly cost for personal use**: $1-5

## �� Security

- Function-level authentication (API keys required)
- Pre-signed blob URLs with expiration
- No secrets stored in source code

## 📄 Related Documentation

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Copilot context
- [iOS_SHORTCUTS_SETUP.md](iOS_SHORTCUTS_SETUP.md) - iOS Shortcuts setup guide

## 📝 License

MIT

## 👤 Author

Kurtis Ingersoll
