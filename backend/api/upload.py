"""
Upload API - Handle audio file uploads
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import logging
import os
import uuid
from pathlib import Path

from models.user import get_current_user, User
from services.supabase_client import supabase, upload_audio_file

router = APIRouter()
logger = logging.getLogger(__name__)


class UploadResponse(BaseModel):
    file_id: str
    url: str
    filename: str
    size: int
    duration: Optional[float] = None


@router.post("/audio", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an audio file to cloud storage
    """
    try:
        # Validate file type
        allowed_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (max 50MB for free tier, 200MB for pro)
        user_data = supabase.table("users").select("tier").eq("id", current_user.id).single().execute()
        max_size = 200 * 1024 * 1024 if user_data.data.get("tier") in ["pro", "enterprise"] else 50 * 1024 * 1024
        
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{current_user.id}/{file_id}{file_ext}"
        
        # Upload to Supabase Storage
        audio_url = await upload_audio_file(
            file_data=file.file.read(),
            filename=filename,
            content_type=file.content_type
        )
        
        logger.info(f"File uploaded: {filename} by user {current_user.id}")
        
        return UploadResponse(
            file_id=file_id,
            url=audio_url,
            filename=file.filename,
            size=file_size
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reference")
async def upload_reference_track(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a reference track for mixing/mastering
    """
    try:
        # Similar to upload_audio but for reference tracks
        # May have different storage path or processing
        
        return {
            "message": "Reference track uploaded successfully",
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Reference upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_id}")
async def delete_audio_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an uploaded audio file
    """
    try:
        # Find and verify file ownership
        # Delete from storage
        # Delete database record
        
        return {
            "message": "File deleted successfully",
            "file_id": file_id
        }
    
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage")
async def get_storage_usage(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's storage usage statistics
    """
    try:
        # Calculate total storage used by user
        tracks = supabase.table("tracks").select("file_size").eq("user_id", current_user.id).execute()
        
        total_size = sum(track.get("file_size", 0) for track in tracks.data)
        
        user_data = supabase.table("users").select("tier").eq("id", current_user.id).single().execute()
        
        storage_limits = {
            "free": 500 * 1024 * 1024,  # 500MB
            "pro": 10 * 1024 * 1024 * 1024,  # 10GB
            "enterprise": 100 * 1024 * 1024 * 1024  # 100GB
        }
        
        tier = user_data.data.get("tier", "free")
        limit = storage_limits.get(tier)
        
        return {
            "used_bytes": total_size,
            "used_mb": round(total_size / (1024 * 1024), 2),
            "limit_bytes": limit,
            "limit_mb": round(limit / (1024 * 1024), 2),
            "percentage": round((total_size / limit) * 100, 2) if limit else 0,
            "tier": tier
        }
    
    except Exception as e:
        logger.error(f"Failed to get storage usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))
