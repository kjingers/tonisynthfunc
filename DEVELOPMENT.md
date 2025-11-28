# Development Guide

This guide covers local development, deployment, and maintenance for the Toni TTS Azure Functions backend.

## 🖥️ Local Development

### Prerequisites

- **Python**: 3.11 or higher
- **Azure Functions Core Tools**: v4
- **Azure CLI**: For deployment and configuration
- **VS Code**: Recommended with Azure Functions extension

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/kjingers/tonisynthfunc.git
cd tonisynthfunc
```

2. **Create virtual environment:**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create local.settings.json:**
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

> ⚠️ Never commit `local.settings.json` to version control.

5. **Run locally:**
```bash
func start
```

The API will be available at `http://localhost:7071/api`

### Getting Azure Credentials

**Speech Service Key:**
```bash
az cognitiveservices account keys list \
  --name <speech-service-name> \
  --resource-group <resource-group>
```

**Storage Account Key:**
```bash
az storage account keys list \
  --account-name <storage-account-name> \
  --resource-group <resource-group>
```

**Function Keys:**
```bash
az functionapp function keys list \
  --name tonisynthfunc \
  --resource-group <resource-group> \
  --function-name batch-start
```

## 🚀 Deployment

### Deploy to Azure

1. **Login to Azure:**
```bash
az login
```

2. **Deploy the function app:**
```bash
func azure functionapp publish tonisynthfunc
```

### Create Resources (New Setup)

If setting up from scratch:

```bash
# Create resource group
az group create --name toni-rg --location westus3

# Create storage account
az storage account create \
  --name tonistorage \
  --resource-group toni-rg \
  --location westus3 \
  --sku Standard_LRS

# Create speech service
az cognitiveservices account create \
  --name toni-speech \
  --resource-group toni-rg \
  --kind SpeechServices \
  --sku S0 \
  --location eastus

# Create function app
az functionapp create \
  --name tonisynthfunc \
  --resource-group toni-rg \
  --consumption-plan-location westus3 \
  --runtime python \
  --runtime-version 3.11 \
  --storage-account tonistorage \
  --functions-version 4

# Configure app settings
az functionapp config appsettings set \
  --name tonisynthfunc \
  --resource-group toni-rg \
  --settings \
    SPEECH_SERVICE_KEY=<key> \
    SPEECH_SERVICE_REGION=eastus \
    STORAGE_ACCOUNT_NAME=tonistorage \
    STORAGE_ACCOUNT_KEY=<key> \
    STORAGE_CONTAINER_NAME=audiofilestoni
```

## 🔧 Configuration

### Voice Configuration (`story_config.py`)

```python
# Default voice and style
DEFAULT_VOICE = "en-US-GuyNeural"
DEFAULT_STYLE = "hopeful"

# Audio format
OUTPUT_FORMAT = "audio-48khz-192kbitrate-mono-mp3"

# URL expiration
SAS_URL_EXPIRY_HOURS = 24
```

### Available Voices

| Voice ID | Description |
|----------|-------------|
| `en-US-GuyNeural` | US Male (default) |
| `en-US-JennyNeural` | US Female |
| `en-US-AriaNeural` | US Female |
| `en-US-DavisNeural` | US Male |
| ... | See Azure docs for full list |

### Available Styles

| Style | Description |
|-------|-------------|
| `hopeful` | Optimistic tone |
| `cheerful` | Happy, upbeat |
| `excited` | Energetic |
| `whispering` | Soft, quiet |
| `sad` | Melancholic |
| ... | See Azure docs for full list |

## 🧪 Testing

### Test with cURL

**Start synthesis:**
```bash
curl -X POST "http://localhost:7071/api/batch-start" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test.", "voice": "en-US-GuyNeural"}'
```

**Check status:**
```bash
curl "http://localhost:7071/api/batch-check?synthesis_id=<id>"
```

### Test with PowerShell

```powershell
$body = @{
    text = "Hello, this is a test."
    voice = "en-US-GuyNeural"
    style = "hopeful"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7071/api/batch-start" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

## 💰 Disabling Resources

### Stop Function App (Pause)

```bash
# Stop (no execution, minimal cost)
az functionapp stop --name tonisynthfunc --resource-group <rg>

# Start again
az functionapp start --name tonisynthfunc --resource-group <rg>
```

### Delete All Resources (Complete Removal)

```bash
# Delete entire resource group (removes everything)
az group delete --name <resource-group> --yes
```

### Disable Frontend Only

See the [tonisynthfunc-web](https://github.com/kjingers/tonisynthfunc-web) README for instructions on disabling the web and iOS frontends.

## 🐛 Troubleshooting

### Common Issues

**"SPEECH_SERVICE_KEY not found"**
- Ensure `local.settings.json` has the key configured
- For deployed app, check Azure Portal → Configuration → Application settings

**Synthesis times out**
- Large texts (>50k chars) may take 5+ minutes
- Increase polling interval or wait time

**CORS errors**
- Add your domain to CORS whitelist in Azure Portal
- Function Apps → CORS → Add origin

### View Logs

**Local:**
```bash
func start --verbose
```

**Azure:**
```bash
az functionapp log tail --name tonisynthfunc --resource-group <rg>
```

Or use Azure Portal → Function App → Log stream

## 📚 Resources

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Speech Service Documentation](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [Batch Synthesis API](https://docs.microsoft.com/azure/cognitive-services/speech-service/batch-synthesis)

## 🚧 Future Enhancements

Ideas for improvement:

1. **Queue-based processing**: Use Azure Queue for better reliability
2. **WebSocket updates**: Real-time synthesis progress
3. **Voice cloning**: Custom voice support
4. **SSML editor**: Advanced speech markup
5. **Caching**: Cache frequently requested texts
6. **Rate limiting**: Prevent abuse
