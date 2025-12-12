"""
Vocal Generation API - Add AI-generated vocals to tracks
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional
import logging

from workers.song_tasks import generate_vocals_task
from models.user import get_current_user, User
from services.supabase_client import supabase

router = APIRouter()
logger = logging.getLogger(__name__)


class VocalGenerateRequest(BaseModel):
    track_id: str
    lyrics: str = Field(..., min_length=10, max_length=2000)
    voice_style: str = Field("pop-female", description="Voice style preset")
    pitch_shift: int = Field(0, ge=-12, le=12, description="Semitone shift")
    vocal_effects: Optional[str] = Field(None, description="Effects to apply")


class VocalGenerateResponse(BaseModel):
    task_id: str
    track_id: str
    status: str
    message: str


@router.post("/generate", response_model=VocalGenerateResponse)
async def generate_vocals(
    request: VocalGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI vocals for an instrumental track
    """
    try:
        logger.info(f"Vocal generation request for track {request.track_id}")
        
        # Verify track ownership
        track = supabase.table("tracks").select("*").eq("id", request.track_id).eq("user_id", current_user.id).single().execute()
        
        if not track.data:
            raise HTTPException(status_code=404, detail="Track not found")
        
        if track.data.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Track generation not completed")
        
        # Queue vocal generation task
        task = generate_vocals_task.delay(
            track_id=request.track_id,
            lyrics=request.lyrics,
            voice_style=request.voice_style,
            pitch_shift=request.pitch_shift,
            vocal_effects=request.vocal_effects
        )
        
        # Update track status
        supabase.table("tracks").update({
            "status": "adding_vocals",
            "lyrics": request.lyrics
        }).eq("id", request.track_id).execute()
        
        return VocalGenerateResponse(
            task_id=task.id,
            track_id=request.track_id,
            status="queued",
            message="Vocal generation started"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vocal generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def list_voice_styles():
    """
    List available voice styles and presets
    """
    return {
        "voice_styles": [
            {
                "id": "pop-female",
                "name": "Pop Female",
                "description": "Modern pop female voice",
                "gender": "female",
                "genre": "pop"
            },
            {
                "id": "pop-male",
                "name": "Pop Male",
                "description": "Modern pop male voice",
                "gender": "male",
                "genre": "pop"
            },
            {
                "id": "rap-male",
                "name": "Rap Male",
                "description": "Hip hop/rap male voice",
                "gender": "male",
                "genre": "hip-hop"
            },
            {
                "id": "soul-female",
                "name": "Soul Female",
                "description": "Soulful R&B female voice",
                "gender": "female",
                "genre": "r&b"
            },
            {
                "id": "rock-male",
                "name": "Rock Male",
                "description": "Powerful rock male voice",
                "gender": "male",
                "genre": "rock"
            }
        ]
    }


@router.post("/clone")
async def clone_voice(
    voice_sample: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Clone a voice from an uploaded sample (Pro feature)
    """
    # Check user tier
    user_data = supabase.table("users").select("tier").eq("id", current_user.id).single().execute()
    
    if user_data.data.get("tier") == "free":
        raise HTTPException(
            status_code=403,
            detail="Voice cloning is a Pro feature. Please upgrade your plan."
        )
    
    try:
        # Save voice sample
        # Process voice cloning
        # Return voice_id for future use
        
        return {
            "message": "Voice cloning initiated",
            "status": "processing"
        }
    
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
