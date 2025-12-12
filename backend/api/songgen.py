"""
Song Generation API - Generate instrumental music from prompts
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import logging

from workers.song_tasks import generate_song_task
from models.user import get_current_user, User
from models.track import TrackCreate, TrackResponse
from services.supabase_client import supabase

router = APIRouter()
logger = logging.getLogger(__name__)


class SongGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=500)
    duration: int = Field(30, ge=10, le=180, description="Duration in seconds")
    model: str = Field("musicgen-medium", description="Model to use")
    temperature: float = Field(1.0, ge=0.1, le=2.0)


class SongGenerateResponse(BaseModel):
    task_id: str
    status: str
    estimated_time: int
    message: str


@router.post("/generate", response_model=SongGenerateResponse)
async def generate_song(
    request: SongGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Generate an instrumental track from a text prompt using AI music generation
    """
    try:
        logger.info(f"Song generation request from user {current_user.id}")
        
        # Check user's generation quota
        user_data = supabase.table("users").select("generation_count, tier").eq("id", current_user.id).single().execute()
        
        generation_limits = {
            "free": 5,
            "pro": 100,
            "enterprise": -1  # unlimited
        }
        
        tier = user_data.data.get("tier", "free")
        count = user_data.data.get("generation_count", 0)
        
        if tier != "enterprise" and count >= generation_limits.get(tier, 5):
            raise HTTPException(
                status_code=429,
                detail="Generation quota exceeded. Please upgrade your plan."
            )
        
        # Create track record
        track_data = {
            "user_id": current_user.id,
            "title": f"Generated Track {count + 1}",
            "prompt": request.prompt,
            "duration": request.duration,
            "status": "generating",
            "type": "instrumental"
        }
        
        track_result = supabase.table("tracks").insert(track_data).execute()
        track_id = track_result.data[0]["id"]
        
        # Queue generation task
        task = generate_song_task.delay(
            track_id=track_id,
            prompt=request.prompt,
            duration=request.duration,
            model=request.model,
            temperature=request.temperature
        )
        
        # Update generation count
        supabase.table("users").update({
            "generation_count": count + 1
        }).eq("id", current_user.id).execute()
        
        estimated_time = request.duration * 2  # Rough estimate
        
        return SongGenerateResponse(
            task_id=task.id,
            status="queued",
            estimated_time=estimated_time,
            message=f"Your track is being generated. Track ID: {track_id}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Song generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_generation_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of a song generation task
    """
    from workers.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task.state,
        "progress": 0
    }
    
    if task.state == "PROGRESS":
        response["progress"] = task.info.get("progress", 0)
        response["message"] = task.info.get("message", "")
    elif task.state == "SUCCESS":
        response["progress"] = 100
        response["result"] = task.info
    elif task.state == "FAILURE":
        response["error"] = str(task.info)
    
    return response


@router.get("/models")
async def list_models():
    """
    List available music generation models
    """
    return {
        "models": [
            {
                "id": "musicgen-small",
                "name": "MusicGen Small",
                "description": "Fast generation, good quality",
                "max_duration": 30,
                "speed": "fast"
            },
            {
                "id": "musicgen-medium",
                "name": "MusicGen Medium",
                "description": "Balanced quality and speed",
                "max_duration": 60,
                "speed": "medium"
            },
            {
                "id": "musicgen-large",
                "name": "MusicGen Large",
                "description": "Highest quality, slower",
                "max_duration": 180,
                "speed": "slow"
            }
        ]
    }
