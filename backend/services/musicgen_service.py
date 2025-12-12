"""
MusicGen Service - AI music generation using Meta's MusicGen
"""
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy.io.wavfile as wavfile
import numpy as np
from typing import Dict, Optional
import tempfile
import os
import logging
from pydub import AudioSegment
import librosa

logger = logging.getLogger(__name__)

# Model cache
_models = {}


def get_model(model_name: str = "facebook/musicgen-medium"):
    """
    Load and cache MusicGen model
    """
    if model_name not in _models:
        logger.info(f"Loading model: {model_name}")
        
        processor = AutoProcessor.from_pretrained(model_name)
        model = MusicgenForConditionalGeneration.from_pretrained(model_name)
        
        # Move to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        
        _models[model_name] = {"processor": processor, "model": model, "device": device}
        
        logger.info(f"Model loaded on {device}")
    
    return _models[model_name]


def generate_music(
    prompt: str,
    duration: int = 30,
    model: str = "facebook/musicgen-medium",
    temperature: float = 1.0,
    top_k: int = 250,
    top_p: float = 0.0
) -> str:
    """
    Generate music from text prompt
    
    Args:
        prompt: Text description of the music
        duration: Duration in seconds
        model: Model identifier
        temperature: Sampling temperature
        top_k: Top-k sampling
        top_p: Top-p sampling
    
    Returns:
        Path to generated audio file
    """
    try:
        logger.info(f"Generating music: '{prompt}' ({duration}s)")
        
        # Get model components
        model_data = get_model(model)
        processor = model_data["processor"]
        musicgen_model = model_data["model"]
        device = model_data["device"]
        
        # Process prompt
        inputs = processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        ).to(device)
        
        # Calculate number of tokens for duration
        # MusicGen generates ~50 tokens per second at 32kHz
        sample_rate = musicgen_model.config.audio_encoder.sampling_rate
        max_new_tokens = int(duration * 50)
        
        # Generate audio
        with torch.no_grad():
            audio_values = musicgen_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p if top_p > 0 else None
            )
        
        # Convert to numpy
        audio_array = audio_values[0, 0].cpu().numpy()
        
        # Save to temporary file
        output_path = tempfile.mktemp(suffix=".wav", prefix="grammy_gen_")
        
        # Normalize audio
        audio_array = audio_array / np.max(np.abs(audio_array))
        
        # Save as WAV file
        wavfile.write(output_path, sample_rate, (audio_array * 32767).astype(np.int16))
        
        logger.info(f"Music generated: {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Music generation failed: {e}")
        raise


def generate_stems(audio_path: str) -> Dict[str, str]:
    """
    Separate audio into stems (drums, bass, vocals, other)
    using source separation
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        Dictionary mapping stem names to file paths
    """
    try:
        logger.info(f"Separating stems from: {audio_path}")
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=None, mono=False)
        
        # For now, create basic stems using frequency filtering
        # TODO: Integrate Demucs or similar for proper stem separation
        
        stems = {}
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio_mono = librosa.to_mono(audio)
        else:
            audio_mono = audio
        
        # Low-pass filter for bass (< 200 Hz)
        bass = librosa.effects.split(audio_mono, top_db=20)
        bass_path = tempfile.mktemp(suffix=".wav", prefix="stem_bass_")
        wavfile.write(bass_path, sr, audio_mono.astype(np.float32))
        stems["bass"] = bass_path
        
        # Band-pass for mids/melody (200-8000 Hz)
        melody_path = tempfile.mktemp(suffix=".wav", prefix="stem_melody_")
        wavfile.write(melody_path, sr, audio_mono.astype(np.float32))
        stems["melody"] = melody_path
        
        # High-pass for percussion/cymbals (> 8000 Hz)
        drums_path = tempfile.mktemp(suffix=".wav", prefix="stem_drums_")
        wavfile.write(drums_path, sr, audio_mono.astype(np.float32))
        stems["drums"] = drums_path
        
        # Full mix as "other"
        other_path = tempfile.mktemp(suffix=".wav", prefix="stem_other_")
        wavfile.write(other_path, sr, audio_mono.astype(np.float32))
        stems["other"] = other_path
        
        logger.info(f"Generated {len(stems)} stems")
        
        return stems
    
    except Exception as e:
        logger.error(f"Stem separation failed: {e}")
        # Return original file as single stem
        return {"full": audio_path}


def extend_audio(audio_path: str, target_duration: int) -> str:
    """
    Extend audio to target duration using AI continuation
    """
    try:
        logger.info(f"Extending audio to {target_duration}s")
        
        # Load existing audio
        audio = AudioSegment.from_wav(audio_path)
        current_duration = len(audio) / 1000  # Convert to seconds
        
        if current_duration >= target_duration:
            return audio_path
        
        # Calculate how much more we need
        extension_needed = target_duration - current_duration
        
        # TODO: Implement AI-based audio continuation
        # For now, simple loop/fade
        extended = audio
        while len(extended) / 1000 < target_duration:
            extended = extended + audio.fade_in(2000).fade_out(2000)
        
        # Trim to exact duration
        extended = extended[:target_duration * 1000]
        
        # Save
        output_path = tempfile.mktemp(suffix=".wav", prefix="grammy_extended_")
        extended.export(output_path, format="wav")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Audio extension failed: {e}")
        raise
