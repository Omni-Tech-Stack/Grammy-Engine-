"""
Celery tasks for song generation and vocal synthesis
"""
from workers.celery_app import celery_app
from workers.base import CallbackTask
from services.musicgen_service import generate_music, generate_stems
from services.vocalsvc_service import generate_vocals, apply_vocal_effects
from services.supabase_client import supabase, upload_audio_file
import logging
import os
from pathlib import Path
import time

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=CallbackTask, name="workers.song_tasks.generate_song_task")
def generate_song_task(self, track_id: str, prompt: str, duration: int, model: str, temperature: float):
    """
    Generate instrumental music from text prompt
    """
    try:
        logger.info(f"Starting song generation for track {track_id}")
        
        # Update progress: Initializing
        self.update_state(
            state="PROGRESS",
            meta={"progress": 10, "message": "Initializing music generation..."}
        )
        
        # Generate music using MusicGen
        self.update_state(
            state="PROGRESS",
            meta={"progress": 30, "message": "Generating audio..."}
        )
        
        audio_path = generate_music(
            prompt=prompt,
            duration=duration,
            model=model,
            temperature=temperature
        )
        
        # Generate individual stems (drums, bass, melody, etc.)
        self.update_state(
            state="PROGRESS",
            meta={"progress": 60, "message": "Separating stems..."}
        )
        
        stems = generate_stems(audio_path)
        
        # Upload to storage
        self.update_state(
            state="PROGRESS",
            meta={"progress": 80, "message": "Uploading files..."}
        )
        
        # Read and upload main audio file
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        audio_url = upload_audio_file(
            file_data=audio_data,
            filename=f"tracks/{track_id}/master.wav",
            content_type="audio/wav"
        )
        
        # Upload stems
        stem_urls = {}
        for stem_name, stem_path in stems.items():
            with open(stem_path, "rb") as f:
                stem_data = f.read()
            
            stem_url = upload_audio_file(
                file_data=stem_data,
                filename=f"tracks/{track_id}/stems/{stem_name}.wav",
                content_type="audio/wav"
            )
            stem_urls[stem_name] = stem_url
        
        # Update track in database
        supabase.table("tracks").update({
            "status": "completed",
            "audio_url": audio_url,
            "stem_urls": stem_urls,
            "completed_at": "now()"
        }).eq("id", track_id).execute()
        
        # Cleanup local files
        os.remove(audio_path)
        for stem_path in stems.values():
            os.remove(stem_path)
        
        logger.info(f"Song generation completed for track {track_id}")
        
        return {
            "track_id": track_id,
            "audio_url": audio_url,
            "stem_urls": stem_urls,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Song generation failed for track {track_id}: {e}")
        
        # Update track status to failed
        supabase.table("tracks").update({
            "status": "failed",
            "error_message": str(e)
        }).eq("id", track_id).execute()
        
        raise


@celery_app.task(bind=True, base=CallbackTask, name="workers.song_tasks.generate_vocals_task")
def generate_vocals_task(
    self,
    track_id: str,
    lyrics: str,
    voice_style: str,
    pitch_shift: int = 0,
    vocal_effects: str = None
):
    """
    Generate AI vocals and mix with instrumental
    """
    try:
        logger.info(f"Starting vocal generation for track {track_id}")
        
        # Get track data
        track = supabase.table("tracks").select("audio_url").eq("id", track_id).single().execute()
        
        if not track.data:
            raise ValueError(f"Track {track_id} not found")
        
        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={"progress": 20, "message": "Generating vocals..."}
        )
        
        # Generate vocals
        vocal_path = generate_vocals(
            lyrics=lyrics,
            voice_style=voice_style,
            duration=None  # Auto-detect from instrumental
        )
        
        # Apply effects
        if vocal_effects or pitch_shift != 0:
            self.update_state(
                state="PROGRESS",
                meta={"progress": 50, "message": "Applying vocal effects..."}
            )
            
            vocal_path = apply_vocal_effects(
                vocal_path,
                pitch_shift=pitch_shift,
                effects=vocal_effects
            )
        
        # Mix vocals with instrumental
        self.update_state(
            state="PROGRESS",
            meta={"progress": 70, "message": "Mixing vocals with instrumental..."}
        )
        
        # TODO: Implement mixing logic
        # For now, just upload vocal track separately
        
        # Upload vocal track
        self.update_state(
            state="PROGRESS",
            meta={"progress": 85, "message": "Uploading..."}
        )
        
        with open(vocal_path, "rb") as f:
            vocal_data = f.read()
        
        vocal_url = upload_audio_file(
            file_data=vocal_data,
            filename=f"tracks/{track_id}/vocals.wav",
            content_type="audio/wav"
        )
        
        # Update track
        supabase.table("tracks").update({
            "status": "completed",
            "vocal_url": vocal_url,
            "has_vocals": True
        }).eq("id", track_id).execute()
        
        # Cleanup
        os.remove(vocal_path)
        
        logger.info(f"Vocal generation completed for track {track_id}")
        
        return {
            "track_id": track_id,
            "vocal_url": vocal_url,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Vocal generation failed for track {track_id}: {e}")
        
        supabase.table("tracks").update({
            "status": "failed",
            "error_message": str(e)
        }).eq("id", track_id).execute()
        
        raise


@celery_app.task(name="workers.song_tasks.cleanup_old_files")
def cleanup_old_files():
    """
    Periodic task to cleanup old temporary files
    """
    try:
        temp_dir = Path("/tmp")
        cutoff_time = time.time() - (24 * 3600)  # 24 hours ago
        
        for file_path in temp_dir.glob("grammy_*"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                logger.info(f"Deleted old temp file: {file_path}")
        
        return {"cleaned_files": "success"}
    
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise
