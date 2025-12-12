"""
Prompt Engine API - Transform user prompts into production-ready music prompts
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from services.openai_service import enhance_prompt, analyze_genre
from models.prompt import PromptCreate, PromptResponse
from models.user import get_current_user, User

router = APIRouter()
logger = logging.getLogger(__name__)


class PromptEnhanceRequest(BaseModel):
    user_input: str = Field(..., description="Raw user prompt")
    style: Optional[str] = Field(None, description="Music style preference")
    mood: Optional[str] = Field(None, description="Desired mood")
    tempo: Optional[int] = Field(None, ge=40, le=200, description="BPM")
    instruments: Optional[List[str]] = Field(None, description="Preferred instruments")


class PromptEnhanceResponse(BaseModel):
    enhanced_prompt: str
    genre: str
    mood: str
    tempo: int
    key: str
    structure: str
    confidence_score: float


@router.post("/enhance", response_model=PromptEnhanceResponse)
async def enhance_user_prompt(
    request: PromptEnhanceRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Transform a user's simple prompt into a detailed, production-ready music prompt
    using AI enhancement and music theory knowledge.
    """
    try:
        logger.info(f"Enhancing prompt for user {current_user.id}: {request.user_input}")
        
        # Enhance the prompt with OpenAI
        enhanced_result = await enhance_prompt(
            user_input=request.user_input,
            style=request.style,
            mood=request.mood,
            tempo=request.tempo,
            instruments=request.instruments
        )
        
        return PromptEnhanceResponse(**enhanced_result)
    
    except Exception as e:
        logger.error(f"Prompt enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_prompt(
    prompt: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a music prompt and extract musical characteristics
    """
    try:
        analysis = await analyze_genre(prompt)
        return {
            "prompt": prompt,
            "analysis": analysis,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Prompt analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_prompt_templates():
    """
    Get pre-built prompt templates for various music styles
    """
    templates = {
        "hip_hop": {
            "name": "Hip Hop Banger",
            "template": "Hard-hitting hip hop beat, 808 bass, crisp snares, {bpm} BPM, {mood} vibes, trap-influenced with {instruments}",
            "default_bpm": 140,
            "default_mood": "aggressive",
            "default_instruments": ["808", "hi-hats", "snare"]
        },
        "pop": {
            "name": "Modern Pop Hit",
            "template": "Catchy pop track, uplifting melody, {bpm} BPM, {mood} atmosphere, radio-ready with {instruments}",
            "default_bpm": 120,
            "default_mood": "energetic",
            "default_instruments": ["synths", "drums", "bass"]
        },
        "edm": {
            "name": "EDM Anthem",
            "template": "High-energy EDM, massive drop, {bpm} BPM, {mood} energy, festival-ready with {instruments}",
            "default_bpm": 128,
            "default_mood": "euphoric",
            "default_instruments": ["synths", "kick", "bass"]
        },
        "lofi": {
            "name": "Lo-Fi Chill",
            "template": "Relaxing lo-fi beats, vinyl crackle, {bpm} BPM, {mood} vibes, study music with {instruments}",
            "default_bpm": 85,
            "default_mood": "chill",
            "default_instruments": ["piano", "drums", "ambient"]
        },
        "rock": {
            "name": "Rock Anthem",
            "template": "Powerful rock track, distorted guitars, {bpm} BPM, {mood} energy, arena-ready with {instruments}",
            "default_bpm": 120,
            "default_mood": "intense",
            "default_instruments": ["electric guitar", "drums", "bass"]
        }
    }
    
    return {"templates": templates}
