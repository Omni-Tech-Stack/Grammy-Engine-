"""
Matchering Service - Professional audio mastering
"""
import subprocess
import tempfile
import os
import logging
from typing import Optional, Dict
import numpy as np
import librosa
import soundfile as sf
from scipy import signal

logger = logging.getLogger(__name__)


def master_track(
    input_path: str,
    reference_path: Optional[str] = None,
    target_loudness: float = -14.0,
    compression: str = "medium",
    eq_preset: str = "balanced",
    stereo_width: float = 1.0
) -> str:
    """
    Master an audio track to professional standards
    
    Args:
        input_path: Path to input audio
        reference_path: Optional reference track for matching
        target_loudness: Target LUFS
        compression: Compression level
        eq_preset: EQ preset name
        stereo_width: Stereo width multiplier
    
    Returns:
        Path to mastered audio file
    """
    try:
        logger.info(f"Mastering track: {input_path}")
        
        # Load audio
        audio, sr = librosa.load(input_path, sr=None, mono=False)
        
        # Ensure stereo
        if len(audio.shape) == 1:
            audio = np.array([audio, audio])
        
        # Step 1: EQ
        audio = apply_eq(audio, sr, eq_preset)
        
        # Step 2: Compression
        audio = apply_compression(audio, compression)
        
        # Step 3: Stereo width adjustment
        if stereo_width != 1.0:
            audio = adjust_stereo_width(audio, stereo_width)
        
        # Step 4: Loudness normalization
        audio = normalize_loudness(audio, sr, target_loudness)
        
        # Step 5: Limiting (prevent clipping)
        audio = apply_limiter(audio, threshold=-0.3)
        
        # Save mastered audio
        output_path = tempfile.mktemp(suffix=".wav", prefix="grammy_mastered_")
        sf.write(output_path, audio.T, sr)
        
        logger.info(f"Mastering complete: {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Mastering failed: {e}")
        raise


def apply_eq(audio: np.ndarray, sr: int, preset: str) -> np.ndarray:
    """
    Apply EQ curve based on preset
    """
    logger.info(f"Applying EQ preset: {preset}")
    
    # Define EQ presets (frequency, gain in dB)
    eq_presets = {
        "balanced": [],  # No changes
        "bright": [(8000, 3), (12000, 2)],  # Boost highs
        "warm": [(200, 2), (500, 1.5)],  # Boost low-mids
        "bass-boost": [(60, 4), (120, 3)]  # Boost bass
    }
    
    bands = eq_presets.get(preset, [])
    
    if not bands:
        return audio
    
    # Apply each EQ band
    for freq, gain_db in bands:
        # Create bell filter
        gain = 10 ** (gain_db / 20)
        q = 1.0
        
        # Design peaking filter
        b, a = signal.iirpeak(freq, q, sr)
        
        # Apply to each channel
        for i in range(audio.shape[0]):
            audio[i] = signal.filtfilt(b, a, audio[i]) * gain
    
    return audio


def apply_compression(audio: np.ndarray, level: str) -> np.ndarray:
    """
    Apply dynamic range compression
    """
    logger.info(f"Applying compression: {level}")
    
    # Compression parameters by level
    params = {
        "light": {"threshold": 0.6, "ratio": 2.0, "attack": 0.005, "release": 0.1},
        "medium": {"threshold": 0.4, "ratio": 4.0, "attack": 0.003, "release": 0.08},
        "heavy": {"threshold": 0.3, "ratio": 8.0, "attack": 0.001, "release": 0.05},
        "limiting": {"threshold": 0.2, "ratio": 20.0, "attack": 0.0001, "release": 0.03}
    }
    
    p = params.get(level, params["medium"])
    
    # Simple peak compression
    threshold = p["threshold"]
    ratio = p["ratio"]
    
    for i in range(audio.shape[0]):
        # Find peaks above threshold
        peaks = np.abs(audio[i]) > threshold
        
        # Apply compression
        audio[i][peaks] = threshold + (audio[i][peaks] - threshold) / ratio
    
    return audio


def normalize_loudness(audio: np.ndarray, sr: int, target_lufs: float) -> np.ndarray:
    """
    Normalize audio to target LUFS
    """
    logger.info(f"Normalizing to {target_lufs} LUFS")
    
    # Calculate current RMS (simplified LUFS approximation)
    rms = np.sqrt(np.mean(audio ** 2))
    
    # Target RMS for desired LUFS (approximation)
    target_rms = 10 ** ((target_lufs + 23) / 20)
    
    # Calculate gain
    if rms > 0:
        gain = target_rms / rms
    else:
        gain = 1.0
    
    # Apply gain
    audio = audio * gain
    
    return audio


def apply_limiter(audio: np.ndarray, threshold: float = -0.3) -> np.ndarray:
    """
    Apply brick-wall limiter to prevent clipping
    """
    logger.info("Applying limiter")
    
    # Convert dB threshold to linear
    threshold_linear = 10 ** (threshold / 20)
    
    # Clip peaks
    audio = np.clip(audio, -threshold_linear, threshold_linear)
    
    return audio


def adjust_stereo_width(audio: np.ndarray, width: float) -> np.ndarray:
    """
    Adjust stereo width
    
    Args:
        audio: Stereo audio array
        width: Width multiplier (0=mono, 1=normal, 2=wide)
    """
    logger.info(f"Adjusting stereo width: {width}")
    
    if audio.shape[0] != 2:
        return audio
    
    # Mid-side processing
    mid = (audio[0] + audio[1]) / 2
    side = (audio[0] - audio[1]) / 2
    
    # Adjust side width
    side = side * width
    
    # Convert back to stereo
    left = mid + side
    right = mid - side
    
    return np.array([left, right])


def analyze_audio(audio_path: str) -> Dict:
    """
    Analyze audio characteristics
    """
    try:
        logger.info(f"Analyzing audio: {audio_path}")
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=None, mono=True)
        
        # Calculate metrics
        rms = np.sqrt(np.mean(audio ** 2))
        peak = np.max(np.abs(audio))
        
        # Estimate LUFS (simplified)
        lufs = 20 * np.log10(rms) - 23
        
        # Dynamic range
        dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
        
        # Spectral centroid (brightness)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
        
        analysis = {
            "loudness_lufs": float(lufs),
            "peak_level": float(20 * np.log10(peak + 1e-10)),
            "dynamic_range": float(dynamic_range),
            "rms_level": float(20 * np.log10(rms + 1e-10)),
            "spectral_centroid": float(spectral_centroid),
            "sample_rate": int(sr),
            "duration": float(len(audio) / sr)
        }
        
        logger.info(f"Analysis complete: LUFS={lufs:.2f}, DR={dynamic_range:.2f}")
        
        return analysis
    
    except Exception as e:
        logger.error(f"Audio analysis failed: {e}")
        raise
