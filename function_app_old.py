import azure.functions as func
import logging
import json
import os
import uuid
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="tonieboxsynthesize")
def tonieboxsynthesize(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Toniebox synthesis function triggered')
    
    try:
        # Get text from request body
        req_body = req.get_json()
        text = req_body.get('text')
        
        # Optional voice parameter - defaults to male neural voice
        voice_name = req_body.get('voice', 'en-US-GuyNeural')
        
        if not text:
            return func.HttpResponse(
                json.dumps({"error": "No text provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        logging.info(f'Starting synthesis for {len(text)} characters')
        
        # Azure Speech Service configuration from environment variables
        speech_key = os.environ['SPEECH_SERVICE_KEY']
        speech_region = os.environ['SPEECH_SERVICE_REGION']
        
        # Generate unique filename for this synthesis
        audio_filename = f"story_{uuid.uuid4()}.mp3"
        
        # Use standard TTS REST API (not Long Audio API)
        # Note: For texts longer than ~10 minutes of audio or 10,000 characters,
        # consider using the Batch Synthesis API instead
        synthesis_url = f"https://{speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
        
        # Create SSML for synthesis
        ssml = f"""<speak version='1.0' xml:lang='en-US'>
            <voice xml:lang='en-US' name='{voice_name}'>
                {text}
            </voice>
        </speak>"""
        
        # Prepare synthesis request headers
        headers = {
            'Ocp-Apim-Subscription-Key': speech_key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-96kbitrate-mono-mp3',
            'User-Agent': 'TonieboxSynthesisFunction'
        }
        
        # Submit synthesis request (synchronous - returns audio immediately)
        response = requests.post(synthesis_url, headers=headers, data=ssml.encode('utf-8'))
        
        if response.status_code != 200:
            logging.error(f"Synthesis request failed: {response.status_code} - {response.text}")
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
        logging.info(f"Successfully synthesized audio: {len(audio_data)} bytes")
        
        # Upload to your blob storage
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
        
        # Generate SAS URL (valid for 24 hours)
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
        logging.error(f"Error in synthesis function: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
        
# OpenAI voice synthesis function (for future use, currently commented out)
# def synthesize_with_openai(text, voice, filename):
#     """
#     Alternative synthesis using OpenAI's TTS API
#     Requires OPENAI_API_KEY in environment variables
#     
#     OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
#     Models: tts-1 (faster, cheaper) or tts-1-hd (higher quality)
#     """
#     import openai
#     
#     openai.api_key = os.environ['OPENAI_API_KEY']
#     
#     # OpenAI has a limit of ~4096 characters per request
#     # For longer content, you'd need to chunk the text and concatenate audio
#     
#     response = openai.audio.speech.create(
#         model="tts-1-hd",  # or "tts-1" for faster/cheaper
#         voice=voice,
#         input=text
#     )
#     
#     # Upload to blob storage (same process as above)
#     # Return SAS URL
#     pass