"""
Celery tasks for mixing and mastering
"""
from workers.celery_app import celery_app
from workers.base import CallbackTask
from services.matchering_service import master_track, analyze_audio
from services.supabase_client import supabase, upload_audio_file
import logging
import os
import tempfile
import requests

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=CallbackTask, name="workers.mix_tasks.mixmaster_task")
def mixmaster_task(
    self,
    track_id: str,
    reference_track_url: str = None,
    target_loudness: float = -14.0,
    compression: str = "medium",
    eq_preset: str = "balanced",
    stereo_width: float = 1.0
):
    """
    Professional mixing and mastering task
    """
    try:
        logger.info(f"Starting mix/master for track {track_id}")
        
        # Get track audio
        track = supabase.table("tracks").select("audio_url").eq("id", track_id).single().execute()
        
        if not track.data or not track.data.get("audio_url"):
            raise ValueError(f"Track {track_id} audio not found")
        
        # Download audio file
        self.update_state(
            state="PROGRESS",
            meta={"progress": 10, "message": "Downloading audio..."}
        )
        
        audio_url = track.data["audio_url"]
        response = requests.get(audio_url)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(response.content)
            input_path = temp_audio.name
        
        # Download reference track if provided
        reference_path = None
        if reference_track_url:
            self.update_state(
                state="PROGRESS",
                meta={"progress": 20, "message": "Downloading reference..."}
            )
            
            ref_response = requests.get(reference_track_url)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_ref:
                temp_ref.write(ref_response.content)
                reference_path = temp_ref.name
        
        # Master the track
        self.update_state(
            state="PROGRESS",
            meta={"progress": 40, "message": "Mastering audio..."}
        )
        
        output_path = master_track(
            input_path=input_path,
            reference_path=reference_path,
            target_loudness=target_loudness,
            compression=compression,
            eq_preset=eq_preset,
            stereo_width=stereo_width
        )
        
        # Analyze mastered audio
        self.update_state(
            state="PROGRESS",
            meta={"progress": 70, "message": "Analyzing results..."}
        )
        
        analysis = analyze_audio(output_path)
        
        # Upload mastered track
        self.update_state(
            state="PROGRESS",
            meta={"progress": 85, "message": "Uploading mastered track..."}
        )
        
        with open(output_path, "rb") as f:
            mastered_data = f.read()
        
        mastered_url = upload_audio_file(
            file_data=mastered_data,
            filename=f"tracks/{track_id}/mastered.wav",
            content_type="audio/wav"
        )
        
        # Update track in database
        supabase.table("tracks").update({
            "status": "mastered",
            "mastered_url": mastered_url,
            "mastering_analysis": analysis,
            "mastered_at": "now()"
        }).eq("id", track_id).execute()
        
        # Cleanup temporary files
        os.remove(input_path)
        os.remove(output_path)
        if reference_path:
            os.remove(reference_path)
        
        logger.info(f"Mix/master completed for track {track_id}")
        
        return {
            "track_id": track_id,
            "mastered_url": mastered_url,
            "analysis": analysis,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Mix/master failed for track {track_id}: {e}")
        
        supabase.table("tracks").update({
            "status": "failed",
            "error_message": str(e)
        }).eq("id", track_id).execute()
        
        raise


@celery_app.task(bind=True, base=CallbackTask, name="workers.mix_tasks.stem_mixing_task")
def stem_mixing_task(self, track_id: str, stem_levels: dict):
    """
    Mix individual stems with custom levels
    """
    try:
        logger.info(f"Starting stem mixing for track {track_id}")
        
        # Get track stems
        track = supabase.table("tracks").select("stem_urls").eq("id", track_id).single().execute()
        
        if not track.data or not track.data.get("stem_urls"):
            raise ValueError(f"Track {track_id} stems not found")
        
        # Download all stems
        # Mix with specified levels
        # Upload mixed result
        
        # TODO: Implement full stem mixing logic
        
        return {
            "track_id": track_id,
            "status": "mixed"
        }
    
    except Exception as e:
        logger.error(f"Stem mixing failed: {e}")
        raise
