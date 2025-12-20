"""
Storage Cleanup Utility

Functions for cleaning up old audio files from Azure Blob Storage.
Can be run manually or scheduled via Azure Functions timer trigger.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from azure.storage.blob import BlobServiceClient, ContainerClient


def get_blob_service_client() -> BlobServiceClient:
    """Get Azure Blob Storage client"""
    account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
    
    if not account_name or not account_key:
        raise ValueError("STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY must be set")
    
    return BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=account_key
    )


def get_container_client(container_name: Optional[str] = None) -> ContainerClient:
    """Get container client"""
    container = container_name or os.environ.get("STORAGE_CONTAINER_NAME", "audio-files")
    blob_service = get_blob_service_client()
    return blob_service.get_container_client(container)


def list_old_blobs(
    days_old: int = 7,
    container_name: Optional[str] = None
) -> List[dict]:
    """
    List blobs older than specified days.
    
    Args:
        days_old: Delete blobs older than this many days (default: 7)
        container_name: Container to check (default from env)
        
    Returns:
        List of blob info dicts with name, size, last_modified
    """
    container_client = get_container_client(container_name)
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    old_blobs = []
    
    for blob in container_client.list_blobs():
        if blob.last_modified and blob.last_modified.replace(tzinfo=None) < cutoff_date:
            old_blobs.append({
                "name": blob.name,
                "size_bytes": blob.size,
                "last_modified": blob.last_modified.isoformat(),
                "content_type": blob.content_settings.content_type if blob.content_settings else None
            })
    
    return old_blobs


def delete_old_blobs(
    days_old: int = 7,
    container_name: Optional[str] = None,
    dry_run: bool = True
) -> dict:
    """
    Delete blobs older than specified days.
    
    Args:
        days_old: Delete blobs older than this many days (default: 7)
        container_name: Container to clean (default from env)
        dry_run: If True, only report what would be deleted (default: True)
        
    Returns:
        Summary dict with counts and details
    """
    container_client = get_container_client(container_name)
    old_blobs = list_old_blobs(days_old, container_name)
    
    result = {
        "dry_run": dry_run,
        "days_threshold": days_old,
        "blobs_found": len(old_blobs),
        "total_size_bytes": sum(b["size_bytes"] for b in old_blobs),
        "total_size_mb": round(sum(b["size_bytes"] for b in old_blobs) / (1024 * 1024), 2),
        "deleted": [],
        "errors": []
    }
    
    if dry_run:
        result["message"] = f"Would delete {len(old_blobs)} blobs ({result['total_size_mb']} MB)"
        result["blobs"] = old_blobs
        return result
    
    for blob_info in old_blobs:
        try:
            container_client.delete_blob(blob_info["name"])
            result["deleted"].append(blob_info["name"])
            logging.info(f"Deleted blob: {blob_info['name']}")
        except Exception as e:
            error_msg = f"Failed to delete {blob_info['name']}: {str(e)}"
            result["errors"].append(error_msg)
            logging.error(error_msg)
    
    result["message"] = f"Deleted {len(result['deleted'])} of {len(old_blobs)} blobs"
    
    return result


def get_storage_stats(container_name: Optional[str] = None) -> dict:
    """
    Get storage statistics for the container.
    
    Args:
        container_name: Container to analyze (default from env)
        
    Returns:
        Dict with storage statistics
    """
    container_client = get_container_client(container_name)
    
    total_blobs = 0
    total_size = 0
    oldest_blob = None
    newest_blob = None
    
    for blob in container_client.list_blobs():
        total_blobs += 1
        total_size += blob.size or 0
        
        if blob.last_modified:
            if oldest_blob is None or blob.last_modified < oldest_blob:
                oldest_blob = blob.last_modified
            if newest_blob is None or blob.last_modified > newest_blob:
                newest_blob = blob.last_modified
    
    return {
        "container": container_client.container_name,
        "total_blobs": total_blobs,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "total_size_gb": round(total_size / (1024 * 1024 * 1024), 3),
        "oldest_blob": oldest_blob.isoformat() if oldest_blob else None,
        "newest_blob": newest_blob.isoformat() if newest_blob else None,
    }


# CLI interface for manual cleanup
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Clean up old audio files from blob storage")
    parser.add_argument("--days", type=int, default=7, help="Delete blobs older than N days")
    parser.add_argument("--container", type=str, help="Container name (default from env)")
    parser.add_argument("--delete", action="store_true", help="Actually delete (default is dry run)")
    parser.add_argument("--stats", action="store_true", help="Show storage statistics")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    if args.stats:
        stats = get_storage_stats(args.container)
        print(json.dumps(stats, indent=2))
    else:
        result = delete_old_blobs(
            days_old=args.days,
            container_name=args.container,
            dry_run=not args.delete
        )
        print(json.dumps(result, indent=2))
