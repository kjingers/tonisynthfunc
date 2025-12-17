import azure.functions as func
import logging
import json
import os
import uuid
import time
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import requests
import zipfile
import io
from story_config import (
    DEFAULT_VOICE, DEFAULT_STYLE, OUTPUT_FORMAT, SAS_URL_EXPIRY_HOURS, SYNTHESIS_TTL_HOURS,
    FILENAME_MAX_LENGTH, FILENAME_WORD_COUNT
)
from filename_utils import generate_synthesis_id, generate_filename_with_uuid

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="batch-start", methods=["POST"])
def batch_start(req: func.HttpRequest) -> func.HttpResponse:
    """
    Start a batch synthesis job and return immediately with synthesis ID and pre-signed URL.
    Similar to AWS Polly async workflow - returns immediately, check status later.
    Perfect for 20-30 minute bedtime stories!
    """
    logging.info('Route hit: batch-start')
    logging.info('Start synthesis function triggered')
    
    try:
        req_body = req.get_json()
        text = req_body.get('text')
        voice_name = req_body.get('voice', DEFAULT_VOICE)  # Use config default
        style = req_body.get('style', DEFAULT_STYLE)  # Use config default
        
        if not text:
            return func.HttpResponse(
                json.dumps({"error": "No text provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Generate descriptive synthesis ID and filename based on text content
        synthesis_id = generate_synthesis_id(text, FILENAME_MAX_LENGTH, FILENAME_WORD_COUNT)
        audio_filename = f"{synthesis_id}.mp3"
        
        logging.info(f'Starting batch synthesis: {synthesis_id}, {len(text)} chars')
        
        speech_key = os.environ['SPEECH_SERVICE_KEY']
        speech_region = os.environ['SPEECH_SERVICE_REGION']
        
        # Create SSML with optional style support
        if style:
            # Use expressive style (e.g., 'cheerful', 'sad', 'gentle')
            ssml = f"""<speak version='1.0' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>
                <voice name='{voice_name}'>
                    <mstts:express-as style='{style}'>
                        {text}
                    </mstts:express-as>
                </voice>
            </speak>"""
        else:
            # Standard SSML
            ssml = f"""<speak version='1.0' xml:lang='en-US'>
                <voice xml:lang='en-US' name='{voice_name}'>
                    {text}
                </voice>
            </speak>"""
        
        # Use Batch Synthesis API (supports >10 min audio, async)
        batch_api_url = f"https://{speech_region}.api.cognitive.microsoft.com/texttospeech/batchsyntheses/{synthesis_id}"
        
        batch_request = {
            "description": f"Bedtime story {datetime.now().isoformat()}",
            "inputKind": "SSML",
            "inputs": [{"content": ssml}],
            "properties": {
                "outputFormat": OUTPUT_FORMAT,
                "concatenateResult": True,
                "timeToLiveInHours": SYNTHESIS_TTL_HOURS
            }
        }
        
        headers = {
            'Ocp-Apim-Subscription-Key': speech_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.put(
            f"{batch_api_url}?api-version=2024-04-01",
            headers=headers,
            json=batch_request
        )
        
        if response.status_code not in [200, 201]:
            logging.error(f"Batch synthesis failed: {response.status_code} - {response.text}")
            return func.HttpResponse(
                json.dumps({
                    "error": "Batch synthesis request failed",
                    "status_code": response.status_code,
                    "details": response.text
                }),
                status_code=500,
                mimetype="application/json"
            )
        
        job_info = response.json()
        logging.info(f"Batch synthesis created: {synthesis_id}, status: {job_info.get('status')}")
        
        # Generate pre-signed SAS URL (like AWS S3 pre-signed URL)
        blob_service_client = BlobServiceClient(
            account_url=f"https://{os.environ['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net",
            credential=os.environ['STORAGE_ACCOUNT_KEY']
        )
        
        container_name = os.environ.get('STORAGE_CONTAINER_NAME', 'audio-files')
        
        # SAS URL valid for configured hours
        sas_token = generate_blob_sas(
            account_name=os.environ['STORAGE_ACCOUNT_NAME'],
            container_name=container_name,
            blob_name=audio_filename,
            account_key=os.environ['STORAGE_ACCOUNT_KEY'],
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=SAS_URL_EXPIRY_HOURS)
        )
        
        sas_url = f"https://{os.environ['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net/{container_name}/{audio_filename}?{sas_token}"
        
        # Status check URL
        status_check_url = f"https://{req.url.split('/api/')[0]}/api/check-synthesis?synthesis_id={synthesis_id}"
        
        return func.HttpResponse(
            json.dumps({
                "status": "started",
                "synthesis_id": synthesis_id,
                "audio_url": sas_url,  # Pre-signed URL - works once synthesis completes
                "status_check_url": status_check_url,
                "voice": voice_name,
                "text_length": len(text),
                "estimated_duration_minutes": len(text) / 1000 * 0.5,
                "message": "Synthesis started. Audio URL will be available when complete (typically 1-3 min)."
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in start_synthesis: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="batch-check", methods=["GET"])
def batch_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Check synthesis status and upload audio to blob storage when complete.
    POLLS INTERNALLY - waits up to 3 minutes for synthesis to complete.
    iOS Shortcut calls once and waits for response (like AWS Lambda).
    """
    logging.info('Route hit: batch-check')
    logging.info('Check synthesis function triggered')
    
    try:
        synthesis_id = req.params.get('synthesis_id')
        
        if not synthesis_id:
            return func.HttpResponse(
                json.dumps({"error": "synthesis_id parameter required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        speech_key = os.environ['SPEECH_SERVICE_KEY']
        speech_region = os.environ['SPEECH_SERVICE_REGION']
        
        batch_api_url = f"https://{speech_region}.api.cognitive.microsoft.com/texttospeech/batchsyntheses/{synthesis_id}"
        
        headers = {'Ocp-Apim-Subscription-Key': speech_key}
        
        # Poll for up to 3 minutes (18 attempts x 10 seconds)
        max_attempts = 18
        poll_interval = 10  # seconds
        
        for attempt in range(max_attempts):
            if attempt > 0:
                import time
                logging.info(f"Polling attempt {attempt + 1}/{max_attempts}, waiting {poll_interval}s...")
                time.sleep(poll_interval)
            
            response = requests.get(
                f"{batch_api_url}?api-version=2024-04-01",
                headers=headers
            )
            
            if response.status_code == 404:
                return func.HttpResponse(
                    json.dumps({"error": "Synthesis job not found", "synthesis_id": synthesis_id}),
                    status_code=404,
                    mimetype="application/json"
                )
            
            if response.status_code != 200:
                return func.HttpResponse(
                    json.dumps({
                        "error": "Failed to check synthesis status",
                        "status_code": response.status_code,
                        "details": response.text
                    }),
                    status_code=500,
                    mimetype="application/json"
                )
            
            job_status = response.json()
            status = job_status.get('status')
            
            logging.info(f"Synthesis {synthesis_id} status: {status} (attempt {attempt + 1})")
            
            # Still processing - continue polling
            if status in ['Running', 'NotStarted']:
                continue
            
            # Failed
            if status == 'Failed':
                error_details = job_status.get('properties', {}).get('failureReason', 'Unknown error')
                return func.HttpResponse(
                    json.dumps({
                        "status": "failed",
                        "synthesis_id": synthesis_id,
                        "error": error_details
                    }),
                    status_code=500,
                    mimetype="application/json"
                )
            
            # Succeeded - download and upload to blob
            if status == 'Succeeded':
                outputs = job_status.get('outputs', {})
                result_url = outputs.get('result')
                
                if not result_url:
                    return func.HttpResponse(
                        json.dumps({"error": "No result URL in successful job"}),
                        status_code=500,
                        mimetype="application/json"
                    )
                
                # Download ZIP file
                logging.info(f"Downloading results from: {result_url}")
                zip_response = requests.get(result_url, headers=headers)
                
                if zip_response.status_code != 200:
                    return func.HttpResponse(
                        json.dumps({"error": "Failed to download synthesis results"}),
                        status_code=500,
                        mimetype="application/json"
                    )
                
                # Extract audio from ZIP
                zip_data = io.BytesIO(zip_response.content)
                with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                    audio_files = [f for f in zip_ref.namelist() if f.endswith(('.mp3', '.wav'))]
                    
                    if not audio_files:
                        return func.HttpResponse(
                            json.dumps({"error": "No audio file found in results"}),
                            status_code=500,
                            mimetype="application/json"
                        )
                    
                    audio_data = zip_ref.read(audio_files[0])
                    logging.info(f"Extracted audio: {audio_files[0]}, {len(audio_data)} bytes")
                
                # Upload to blob storage
                audio_filename = f"{synthesis_id}.mp3"
                blob_service_client = BlobServiceClient(
                    account_url=f"https://{os.environ['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net",
                    credential=os.environ['STORAGE_ACCOUNT_KEY']
                )
                
                container_name = os.environ.get('STORAGE_CONTAINER_NAME', 'audio-files')
                blob_client = blob_service_client.get_blob_client(
                    container=container_name,
                    blob=audio_filename
                )
                
                blob_client.upload_blob(audio_data, overwrite=True)
                logging.info(f"Uploaded to blob storage: {audio_filename}")
                
                # Generate SAS URL
                sas_token = generate_blob_sas(
                    account_name=os.environ['STORAGE_ACCOUNT_NAME'],
                    container_name=container_name,
                    blob_name=audio_filename,
                    account_key=os.environ['STORAGE_ACCOUNT_KEY'],
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=48)
                )
                
                sas_url = f"https://{os.environ['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net/{container_name}/{audio_filename}?{sas_token}"
                
                properties = job_status.get('properties', {})
                duration_ms = properties.get('durationInMilliseconds', 0)
                size_bytes = properties.get('sizeInBytes', len(audio_data))
                
                return func.HttpResponse(
                    json.dumps({
                        "status": "completed",
                        "synthesis_id": synthesis_id,
                        "audio_url": sas_url,
                        "size_bytes": size_bytes,
                        "duration_seconds": duration_ms / 1000 if duration_ms else None,
                        "message": "Synthesis complete. Audio ready for download."
                    }),
                    status_code=200,
                    mimetype="application/json"
                )
            
            # Unknown status - continue polling
            logging.warning(f"Unknown status: {status}, continuing to poll...")
            continue        # Timeout - synthesis took too long
        return func.HttpResponse(
            json.dumps({
                "status": "timeout",
                "synthesis_id": synthesis_id,
                "message": "Synthesis timeout after 3 minutes. Try again later or check Azure Portal.",
                "elapsed_seconds": max_attempts * poll_interval
            }),
            status_code=408,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in check_synthesis: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="sync-tts", methods=["POST"])
def sync_tts(req: func.HttpRequest) -> func.HttpResponse:
    """
    LEGACY - Synchronous synthesis (up to ~10 min audio / ~5000 chars)
    For bedtime stories, use /api/batch-start instead!
    """
    logging.info('Route hit: sync-tts')
    logging.info('Legacy tonieboxsynthesize endpoint called')
    
    try:
        req_body = req.get_json()
        text = req_body.get('text')
        voice_name = req_body.get('voice', 'en-US-GuyNeural')
        
        if not text:
            return func.HttpResponse(
                json.dumps({"error": "No text provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Redirect long texts to batch API
        if len(text) > 5000:
            return func.HttpResponse(
                json.dumps({
                    "error": "Text too long for synchronous synthesis",
                    "message": "Use /api/batch-start for bedtime stories",
                    "text_length": len(text),
                    "max_length": 5000
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        logging.info(f'Synchronous synthesis: {len(text)} chars')
        
        speech_key = os.environ['SPEECH_SERVICE_KEY']
        speech_region = os.environ['SPEECH_SERVICE_REGION']
        
        # Generate descriptive filename based on text content
        audio_filename = generate_filename_with_uuid(text, FILENAME_MAX_LENGTH, FILENAME_WORD_COUNT)
        
        # Standard TTS REST API
        synthesis_url = f"https://{speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
        
        ssml = f"""<speak version='1.0' xml:lang='en-US'>
            <voice xml:lang='en-US' name='{voice_name}'>
                {text}
            </voice>
        </speak>"""
        
        headers = {
            'Ocp-Apim-Subscription-Key': speech_key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-96kbitrate-mono-mp3',
            'User-Agent': 'TonieboxSynthesisFunction'
        }
        
        response = requests.post(synthesis_url, headers=headers, data=ssml.encode('utf-8'))
        
        if response.status_code != 200:
            logging.error(f"Synthesis failed: {response.status_code}")
            return func.HttpResponse(
                json.dumps({
                    "error": "Synthesis request failed",
                    "status_code": response.status_code,
                    "details": response.text
                }),
                status_code=500,
                mimetype="application/json"
            )
        
        audio_data = response.content
        logging.info(f"Synthesized: {len(audio_data)} bytes")
        
        # Upload to blob
        blob_service_client = BlobServiceClient(
            account_url=f"https://{os.environ['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net",
            credential=os.environ['STORAGE_ACCOUNT_KEY']
        )
        
        container_name = os.environ.get('STORAGE_CONTAINER_NAME', 'audio-files')
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=audio_filename
        )
        
        blob_client.upload_blob(audio_data, overwrite=True)
        logging.info(f"Uploaded: {audio_filename}")
        
        # Generate SAS URL
        sas_token = generate_blob_sas(
            account_name=os.environ['STORAGE_ACCOUNT_NAME'],
            container_name=container_name,
            blob_name=audio_filename,
            account_key=os.environ['STORAGE_ACCOUNT_KEY'],
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=24)
        )
        
        sas_url = f"https://{os.environ['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net/{container_name}/{audio_filename}?{sas_token}"
        
        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "url": sas_url,
                "filename": audio_filename,
                "voice": voice_name,
                "size_bytes": len(audio_data),
                "text_length": len(text)
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
