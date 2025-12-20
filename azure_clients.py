"""
Azure Clients Module

Centralized Azure service client creation and utility functions.
Eliminates duplicate code across function endpoints.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

from story_config import SAS_URL_EXPIRY_HOURS


class ConfigurationError(Exception):
    """Raised when required configuration is missing"""
    pass


class AzureServiceError(Exception):
    """Raised when Azure service call fails"""
    pass


def validate_environment() -> None:
    """
    Validate that all required environment variables are set.
    Should be called at startup.
    
    Raises:
        ConfigurationError: If required env vars are missing
    """
    required_vars = [
        "SPEECH_SERVICE_KEY",
        "SPEECH_SERVICE_REGION",
        "STORAGE_ACCOUNT_NAME",
        "STORAGE_ACCOUNT_KEY",
    ]
    
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing)}"
        )


def get_speech_credentials() -> Tuple[str, str]:
    """
    Get Azure Speech Service credentials.
    
    Returns:
        Tuple of (key, region)
        
    Raises:
        ConfigurationError: If credentials not configured
    """
    key = os.environ.get("SPEECH_SERVICE_KEY")
    region = os.environ.get("SPEECH_SERVICE_REGION")
    
    if not key or not region:
        raise ConfigurationError(
            "SPEECH_SERVICE_KEY and SPEECH_SERVICE_REGION must be set"
        )
    
    return key, region


def get_blob_service_client() -> BlobServiceClient:
    """
    Create and return a BlobServiceClient.
    
    Returns:
        Configured BlobServiceClient
        
    Raises:
        ConfigurationError: If storage credentials not configured
    """
    account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
    
    if not account_name or not account_key:
        raise ConfigurationError(
            "STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY must be set"
        )
    
    return BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=account_key
    )


def get_container_name() -> str:
    """Get the blob container name from environment or default"""
    return os.environ.get("STORAGE_CONTAINER_NAME", "audio-files")


def generate_sas_url(
    blob_name: str,
    expiry_hours: Optional[int] = None
) -> str:
    """
    Generate a SAS URL for a blob.
    
    Args:
        blob_name: Name of the blob
        expiry_hours: Hours until SAS expires (default from config)
        
    Returns:
        Full SAS URL for the blob
    """
    account_name = os.environ["STORAGE_ACCOUNT_NAME"]
    account_key = os.environ["STORAGE_ACCOUNT_KEY"]
    container_name = get_container_name()
    
    hours = expiry_hours or SAS_URL_EXPIRY_HOURS
    
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=hours)
    )
    
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"


def upload_to_blob(
    data: bytes,
    blob_name: str,
    overwrite: bool = True
) -> str:
    """
    Upload data to blob storage.
    
    Args:
        data: Bytes to upload
        blob_name: Name for the blob
        overwrite: Whether to overwrite existing blob
        
    Returns:
        SAS URL for the uploaded blob
    """
    blob_service = get_blob_service_client()
    container_name = get_container_name()
    
    blob_client = blob_service.get_blob_client(
        container=container_name,
        blob=blob_name
    )
    
    blob_client.upload_blob(data, overwrite=overwrite)
    logging.info(f"Uploaded blob: {blob_name}, {len(data)} bytes")
    
    return generate_sas_url(blob_name)


def get_batch_synthesis_url(synthesis_id: str) -> str:
    """
    Get the Azure Speech Batch Synthesis API URL.
    
    Args:
        synthesis_id: The synthesis job ID
        
    Returns:
        Full API URL
    """
    _, region = get_speech_credentials()
    return f"https://{region}.api.cognitive.microsoft.com/texttospeech/batchsyntheses/{synthesis_id}"


def get_speech_headers() -> dict:
    """
    Get headers for Azure Speech API requests.
    
    Returns:
        Dict of headers
    """
    key, _ = get_speech_credentials()
    return {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }
