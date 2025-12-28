"""
Celery tasks for Grammy Meter analysis and hit prediction
"""
from workers.celery_app import celery_app
from workers.base import CallbackTask
from services.hit_score_service import calculate_grammy_score, analyze_trends
from services.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=CallbackTask, name="workers.meter_tasks.analyze_hit_potential_task")
def analyze_hit_potential_task(self, track_id: str):
    """
    Analyze track's hit potential using Grammy Meter
    """
    try:
        logger.info(f"Starting Grammy Meter analysis for track {track_id}")
        
        # Get track data
        track = supabase.table("tracks").select("*").eq("id", track_id).single().execute()
        
        if not track.data:
            raise ValueError(f"Track {track_id} not found")
        
        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={"progress": 20, "message": "Analyzing audio features..."}
        )
        
        # Calculate Grammy Score
        score_result = calculate_grammy_score(
            audio_url=track.data.get("audio_url") or track.data.get("mastered_url"),
            metadata={
                "title": track.data.get("title"),
                "genre": track.data.get("genre"),
                "duration": track.data.get("duration"),
                "prompt": track.data.get("prompt")
            }
        )
        
        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={"progress": 60, "message": "Analyzing market trends..."}
        )
        
        # Analyze trends
        trend_analysis = analyze_trends(
            genre=track.data.get("genre"),
            features=score_result.get("features", {})
        )
        
        # Combine scores
        final_score = {
            **score_result,
            "trend_analysis": trend_analysis,
            "viral_potential": trend_analysis.get("viral_score", 0)
        }
        
        # Save to database
        self.update_state(
            state="PROGRESS",
            meta={"progress": 90, "message": "Saving results..."}
        )
        
        score_data = {
            "track_id": track_id,
            "overall_score": score_result["overall_score"],
            "production_quality": score_result["category_scores"]["production_quality"],
            "commercial_appeal": score_result["category_scores"]["commercial_appeal"],
            "innovation": score_result["category_scores"]["innovation"],
            "emotional_impact": score_result["category_scores"]["emotional_impact"],
            "radio_readiness": score_result["category_scores"]["radio_readiness"],
            "viral_potential": trend_analysis.get("viral_score", 0),
            "insights": score_result["insights"],
            "recommendations": score_result["recommendations"]
        }
        
        supabase.table("grammy_scores").insert(score_data).execute()
        
        # Update track with score
        supabase.table("tracks").update({
            "grammy_score": score_result["overall_score"]
        }).eq("id", track_id).execute()
        
        logger.info(f"Grammy Meter analysis completed for track {track_id}")
        
        return final_score
    
    except Exception as e:
        logger.error(f"Grammy Meter analysis failed for track {track_id}: {e}")
        raise


@celery_app.task(name="workers.meter_tasks.batch_trend_analysis")
def batch_trend_analysis():
    """
    Periodic task to analyze trending tracks
    """
    try:
        logger.info("Starting batch trend analysis")
        
        # Get recent tracks
        tracks = supabase.table("tracks")\
            .select("id, genre, grammy_score")\
            .order("created_at", desc=True)\
            .limit(100)\
            .execute()
        
        # Analyze trends by genre
        genre_trends = {}
        for track in tracks.data:
            genre = track.get("genre", "unknown")
            if genre not in genre_trends:
                genre_trends[genre] = []
            genre_trends[genre].append(track.get("grammy_score", 0))
        
        # Calculate average scores per genre
        trend_data = {}
        for genre, scores in genre_trends.items():
            trend_data[genre] = {
                "avg_score": sum(scores) / len(scores) if scores else 0,
                "count": len(scores),
                "trending": sum(scores) / len(scores) > 70 if scores else False
            }
        
        # Save trends
        supabase.table("trend_data").insert({
            "data": trend_data,
            "analyzed_at": "now()"
        }).execute()
        
        logger.info("Batch trend analysis completed")
        
        return trend_data
    
    except Exception as e:
        logger.error(f"Batch trend analysis failed: {e}")
        raise
