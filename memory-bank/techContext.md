# Tech Context - Toni TTS

## Technologies Used

### Core Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime language |
| Azure Functions | v4 | Serverless compute platform |
| Azure Cognitive Services Speech | - | Neural TTS engine |
| Azure Blob Storage | - | Audio file storage |

### Python Dependencies
```
azure-functions          # Azure Functions SDK
azure-storage-blob       # Blob storage client
requests                 # HTTP client for Azure APIs
```

### Azure Services
| Service | SKU | Region | Notes |
|---------|-----|--------|-------|
| Azure Functions | Consumption Plan | West US 3 | Pay-per-execution |
| Speech Service | S0 | East US | Neural voices |
| Blob Storage | Standard LRS | - | Audio files |

## Development Setup

### Prerequisites
- Python 3.11 or higher
- Azure Functions Core Tools v4
- Azure CLI (for deployment)
- VS Code with Azure Functions extension (recommended)

### Local Development
```bash
# Clone repository
git clone https://github.com/kjingers/tonisynthfunc.git
cd tonisynthfunc

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run locally
func start
```

### Required Environment Variables
Create `local.settings.json` (not in git):
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SPEECH_SERVICE_KEY": "<your-speech-service-key>",
    "SPEECH_SERVICE_REGION": "eastus",
    "STORAGE_ACCOUNT_NAME": "<your-storage-account>",
    "STORAGE_ACCOUNT_KEY": "<your-storage-key>",
    "STORAGE_CONTAINER_NAME": "audiofilestoni"
  }
}
```

## Technical Constraints

### Azure Functions Limits
- **Timeout**: Consumption plan max 10 minutes per execution
- **Memory**: 1.5 GB max per instance
- **Payload**: 100 MB max request size

### Azure Speech Service Limits
- **Synchronous API**: ~10 minutes audio max (~5000 chars)
- **Batch API**: Unlimited (designed for long content)
- **Concurrent jobs**: Limited by subscription tier

### Blob Storage
- **Container**: `audiofilestoni`
- **File format**: MP3 (audio-24khz-96kbitrate-mono-mp3)
- **Retention**: Manual (no auto-delete configured)

## API Reference

### Azure Batch Synthesis API
- **Endpoint**: `https://{region}.api.cognitive.microsoft.com/texttospeech/batchsyntheses/{id}`
- **API Version**: `2024-04-01`
- **Auth**: `Ocp-Apim-Subscription-Key` header

### Key API Operations
```python
# Create synthesis job
PUT /texttospeech/batchsyntheses/{synthesis_id}?api-version=2024-04-01

# Check status
GET /texttospeech/batchsyntheses/{synthesis_id}?api-version=2024-04-01
```

## Deployment

### Deploy to Azure
```bash
az login
func azure functionapp publish tonisynthfunc
```

### Live Endpoint
```
https://tonisynthfunc-aegzcngjgudgcdeh.westus3-01.azurewebsites.net/api
```

### Get Function Keys
```bash
az functionapp function keys list \
  --name tonisynthfunc \
  --resource-group <resource-group> \
  --function-name batch-start
```

## Tool Usage Patterns

### Testing Locally
```bash
# Start synthesis
curl -X POST "http://localhost:7071/api/batch-start" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test.", "voice": "en-US-GuyNeural"}'

# Check status
curl "http://localhost:7071/api/batch-check?synthesis_id=<id>"
```

### Azure CLI Commands
```bash
# View logs
az functionapp log tail --name tonisynthfunc --resource-group <rg>

# Stop function app
az functionapp stop --name tonisynthfunc --resource-group <rg>

# Start function app
az functionapp start --name tonisynthfunc --resource-group <rg>
```

## Project File Structure

```
tonisynthfunc/
├── function_app.py          # Main Azure Functions code (3 endpoints)
├── story_config.py          # Voice/style configuration
├── requirements.txt         # Python dependencies
├── host.json                # Azure Functions host config
├── local.settings.json      # Local dev settings (gitignored)
├── .vscode/
│   └── extensions.json      # Recommended VS Code extensions
├── memory-bank/             # Project documentation
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md       # This file
│   ├── activeContext.md
│   └── progress.md
├── *.md                     # Various guides and documentation
└── *.mp3                    # Sample audio files
```

## Cost Information

| Service | Pricing | Typical Monthly |
|---------|---------|-----------------|
| Azure Functions | Free tier: 1M exec/month | $0 |
| Speech Service | $16 per 1M characters | $1-3 |
| Blob Storage | ~$0.02/GB/month | <$1 |
| **Total** | - | **~$1-5** |
