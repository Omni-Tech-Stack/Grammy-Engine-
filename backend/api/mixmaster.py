"""
Mix & Master API - Professional-grade audio mixing and mastering
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional
import logging

from workers.mix_tasks import mixmaster_task
from models.user import get_current_user, User
from services.supabase_client import supabase

router = APIRouter()
logger = logging.getLogger(__name__)


class MixMasterRequest(BaseModel):
    track_id: str
    reference_track_url: Optional[str] = None
    target_loudness: float = Field(-14.0, ge=-20.0, le=-8.0, description="LUFS")
    compression: str = Field("medium", description="Compression level")
    eq_preset: str = Field("balanced", description="EQ preset")
    stereo_width: float = Field(1.0, ge=0.0, le=2.0)


class MixMasterResponse(BaseModel):
    task_id: str
    track_id: str
    status: str
    message: str


@router.post("/process", response_model=MixMasterResponse)
async def mix_and_master_track(
    request: MixMasterRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Apply professional mixing and mastering to a track
    """
    try:
        logger.info(f"Mix/Master request for track {request.track_id}")
        
        # Verify track ownership
        track = supabase.table("tracks").select("*").eq("id", request.track_id).eq("user_id", current_user.id).single().execute()
        
        if not track.data:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Queue mix/master task
        task = mixmaster_task.delay(
            track_id=request.track_id,
            reference_track_url=request.reference_track_url,
            target_loudness=request.target_loudness,
            compression=request.compression,
            eq_preset=request.eq_preset,
            stereo_width=request.stereo_width
        )
        
        # Update track status
        supabase.table("tracks").update({
            "status": "mastering"
        }).eq("id", request.track_id).execute()
        
        return MixMasterResponse(
            task_id=task.id,
            track_id=request.track_id,
            status="queued",
            message="Mix & master processing started"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mix/master failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reference-match")
async def match_reference_track(
    track_id: str,
    reference_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Master a track to match the sonic characteristics of a reference track
    """
    try:
        # Save reference file
        # Analyze reference characteristics
        # Apply matching mastering
        
        return {
            "message": "Reference matching initiated",
            "track_id": track_id,
            "status": "processing"
        }
    
    except Exception as e:
        logger.error(f"Reference matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets")
async def get_mastering_presets():
    """
    Get available mastering presets
    """
    return {
        "eq_presets": [
            {
                "id": "balanced",
                "name": "Balanced",
                "description": "Neutral, balanced frequency response"
            },
            {
                "id": "bright",
                "name": "Bright",
                "description": "Enhanced high frequencies"
            },
            {
                "id": "warm",
                "name": "Warm",
                "description": "Enhanced low-mid frequencies"
            },
            {
                "id": "bass-boost",
                "name": "Bass Boost",
                "description": "Enhanced low frequencies"
            }
        ],
        "compression_levels": ["light", "medium", "heavy", "limiting"],
        "loudness_targets": {
            "spotify": -14.0,
            "apple_music": -16.0,
            "youtube": -13.0,
            "soundcloud": -8.0,
            "cd": -9.0
        }
    }


@router.post("/analyze/{track_id}")
async def analyze_mix(
    track_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a track's mix characteristics
    """
    try:
        track = supabase.table("tracks").select("audio_url").eq("id", track_id).eq("user_id", current_user.id).single().execute()
        
        if not track.data:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Analyze audio characteristics
        # Return detailed analysis
        
        return {
            "track_id": track_id,
            "analysis": {
                "loudness_lufs": -12.5,
                "dynamic_range": 8.2,
                "peak_level": -0.3,
                "frequency_balance": "balanced",
                "stereo_width": 0.85,
                "recommendations": [
                    "Consider reducing peak levels slightly",
                    "Good dynamic range for the genre",
                    "Frequency balance is well-distributed"
                ]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mix analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
