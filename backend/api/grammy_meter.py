"""
Grammy Meter API - AI-powered hit prediction and scoring
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from workers.meter_tasks import analyze_hit_potential_task
from models.user import get_current_user, User
from services.supabase_client import supabase
from services.hit_score_service import calculate_grammy_score

router = APIRouter()
logger = logging.getLogger(__name__)


class GrammyMeterRequest(BaseModel):
    track_id: str


class GrammyMeterResponse(BaseModel):
    track_id: str
    overall_score: float
    category_scores: Dict[str, float]
    insights: List[str]
    recommendations: List[str]
    comparison: Optional[Dict[str, any]] = None


@router.post("/analyze", response_model=GrammyMeterResponse)
async def analyze_track_potential(
    request: GrammyMeterRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a track's Grammy/hit potential using AI scoring
    """
    try:
        logger.info(f"Grammy Meter analysis for track {request.track_id}")
        
        # Verify track ownership
        track = supabase.table("tracks").select("*").eq("id", request.track_id).eq("user_id", current_user.id).single().execute()
        
        if not track.data:
            raise HTTPException(status_code=404, detail="Track not found")
        
        if not track.data.get("audio_url"):
            raise HTTPException(status_code=400, detail="Track audio not available")
        
        # Calculate Grammy Score
        score_result = await calculate_grammy_score(
            audio_url=track.data["audio_url"],
            metadata={
                "title": track.data.get("title"),
                "genre": track.data.get("genre"),
                "duration": track.data.get("duration")
            }
        )
        
        # Save score to database
        score_data = {
            "track_id": request.track_id,
            "overall_score": score_result["overall_score"],
            "production_quality": score_result["category_scores"]["production_quality"],
            "commercial_appeal": score_result["category_scores"]["commercial_appeal"],
            "innovation": score_result["category_scores"]["innovation"],
            "emotional_impact": score_result["category_scores"]["emotional_impact"],
            "radio_readiness": score_result["category_scores"]["radio_readiness"]
        }
        
        supabase.table("grammy_scores").insert(score_data).execute()
        
        return GrammyMeterResponse(
            track_id=request.track_id,
            overall_score=score_result["overall_score"],
            category_scores=score_result["category_scores"],
            insights=score_result["insights"],
            recommendations=score_result["recommendations"],
            comparison=score_result.get("comparison")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Grammy Meter analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{track_id}")
async def get_score_history(
    track_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get historical Grammy Meter scores for a track
    """
    try:
        scores = supabase.table("grammy_scores")\
            .select("*")\
            .eq("track_id", track_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return {
            "track_id": track_id,
            "scores": scores.data
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch score history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard(
    genre: Optional[str] = None,
    time_period: str = "week",
    limit: int = 20
):
    """
    Get top-scored tracks leaderboard
    """
    try:
        query = supabase.table("tracks")\
            .select("id, title, user_id, genre, grammy_scores(overall_score)")\
            .order("grammy_scores.overall_score", desc=True)\
            .limit(limit)
        
        if genre:
            query = query.eq("genre", genre)
        
        # Apply time filter based on time_period
        # (requires additional date filtering logic)
        
        results = query.execute()
        
        return {
            "leaderboard": results.data,
            "genre": genre,
            "time_period": time_period
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks")
async def get_score_benchmarks():
    """
    Get Grammy Meter scoring benchmarks and thresholds
    """
    return {
        "score_ranges": {
            "grammy_worthy": {"min": 85, "max": 100, "label": "Grammy Worthy"},
            "hit_potential": {"min": 70, "max": 84, "label": "Hit Potential"},
            "radio_ready": {"min": 60, "max": 69, "label": "Radio Ready"},
            "promising": {"min": 45, "max": 59, "label": "Promising"},
            "needs_work": {"min": 0, "max": 44, "label": "Needs Work"}
        },
        "category_weights": {
            "production_quality": 25,
            "commercial_appeal": 30,
            "innovation": 15,
            "emotional_impact": 20,
            "radio_readiness": 10
        },
        "description": "Grammy Meter analyzes your track across multiple dimensions to predict commercial and critical success potential."
    }
