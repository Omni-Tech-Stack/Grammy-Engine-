"""
Hit Score Service - AI-powered Grammy Meter and hit prediction
Optimized for ARM architecture with lightweight processing
"""
import numpy as np
import librosa
import requests
import tempfile
import os
import logging
from typing import Dict, List
from sklearn.preprocessing import StandardScaler
from utils.config import is_lightweight_mode, get_audio_buffer_size

logger = logging.getLogger(__name__)

# Constants for audio feature extraction
HARMONIC_RATIO_SPECTRAL_THRESHOLD = 5000.0  # Hz - Spectral centroid threshold for estimating harmonic content


async def calculate_grammy_score(audio_url: str, metadata: Dict) -> Dict:
    """
    Calculate Grammy Meter score for a track
    
    Analyzes multiple dimensions:
    - Production Quality (mix, mastering, clarity)
    - Commercial Appeal (catchiness, structure)
    - Innovation (uniqueness, creativity)
    - Emotional Impact (mood, energy, dynamics)
    - Radio Readiness (length, format, loudness)
    
    Returns:
        Dictionary with overall score and category breakdown
    """
    try:
        logger.info(f"Calculating Grammy Score for: {metadata.get('title')}")
        
        # Download audio file
        response = requests.get(audio_url)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(response.content)
            audio_path = temp_file.name
        
        # Extract audio features
        features = extract_audio_features(audio_path)
        
        # Calculate category scores
        category_scores = {
            "production_quality": calculate_production_quality(features),
            "commercial_appeal": calculate_commercial_appeal(features, metadata),
            "innovation": calculate_innovation(features),
            "emotional_impact": calculate_emotional_impact(features),
            "radio_readiness": calculate_radio_readiness(features, metadata)
        }
        
        # Calculate weighted overall score
        weights = {
            "production_quality": 0.25,
            "commercial_appeal": 0.30,
            "innovation": 0.15,
            "emotional_impact": 0.20,
            "radio_readiness": 0.10
        }
        
        overall_score = sum(
            category_scores[category] * weight
            for category, weight in weights.items()
        )
        
        # Generate insights
        insights = generate_insights(category_scores, features)
        
        # Generate recommendations
        recommendations = generate_recommendations(category_scores, features)
        
        # Cleanup
        os.remove(audio_path)
        
        result = {
            "overall_score": round(overall_score, 2),
            "category_scores": {k: round(v, 2) for k, v in category_scores.items()},
            "insights": insights,
            "recommendations": recommendations,
            "features": features
        }
        
        logger.info(f"Grammy Score: {overall_score:.2f}")
        
        return result
    
    except Exception as e:
        logger.error(f"Grammy Score calculation failed: {e}")
        raise


def extract_audio_features(audio_path: str) -> Dict:
    """
    Extract comprehensive audio features for analysis
    Optimized for lightweight mode with reduced feature extraction
    """
    try:
        # Load audio with optimized buffer size
        buffer_size = get_audio_buffer_size()
        
        # In lightweight mode, use lower sample rate for faster processing
        target_sr = 22050 if is_lightweight_mode() else None
        
        y, sr = librosa.load(audio_path, sr=target_sr)
        
        # Basic features
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Tempo calculation with hop_length optimization
        hop_length = 1024 if is_lightweight_mode() else 512
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
        
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=hop_length))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y, hop_length=hop_length))
        
        # Energy and dynamics
        rms = librosa.feature.rms(y=y, hop_length=hop_length)
        rms_mean = np.mean(rms)
        rms_std = np.std(rms)
        dynamic_range = 20 * np.log10(np.max(rms) / (np.min(rms) + 1e-10))
        
        # In lightweight mode, skip expensive harmonic/percussive separation
        if is_lightweight_mode():
            # Estimate harmonic ratio from spectral features instead
            harmonic_ratio = min(1.0, spectral_centroid / HARMONIC_RATIO_SPECTRAL_THRESHOLD)
            logger.info("Lightweight mode: Using estimated harmonic ratio")
        else:
            # Full harmonic and percussive separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            harmonic_ratio = np.mean(np.abs(y_harmonic)) / (np.mean(np.abs(y)) + 1e-10)
        
        # Skip MFCC and chroma in lightweight mode to save processing time
        if not is_lightweight_mode():
            # Chroma and key
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
            chroma_mean = np.mean(chroma, axis=1)
            
            # MFCC for timbre
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop_length)
            mfcc_mean = np.mean(mfcc, axis=1)
        
        # Loudness (simplified LUFS)
        loudness = 20 * np.log10(rms_mean + 1e-10) - 23
        
        features = {
            "duration": float(duration),
            "tempo": float(tempo),
            "spectral_centroid": float(spectral_centroid),
            "spectral_rolloff": float(spectral_rolloff),
            "zero_crossing_rate": float(zero_crossing_rate),
            "rms_mean": float(rms_mean),
            "rms_std": float(rms_std),
            "dynamic_range": float(dynamic_range),
            "harmonic_ratio": float(harmonic_ratio),
            "loudness": float(loudness),
            "beat_count": int(len(beats))
        }
        
        return features
    
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        raise


def calculate_production_quality(features: Dict) -> float:
    """
    Score production quality (0-100)
    """
    score = 50.0  # Base score
    
    # Loudness check (target -14 LUFS)
    loudness_diff = abs(features["loudness"] - (-14.0))
    score += max(0, 15 - loudness_diff * 2)
    
    # Dynamic range (8-12 dB is good)
    dr = features["dynamic_range"]
    if 8 <= dr <= 12:
        score += 20
    elif 6 <= dr <= 14:
        score += 10
    
    # Spectral balance
    if 2000 <= features["spectral_centroid"] <= 4000:
        score += 15
    
    return min(100, max(0, score))


def calculate_commercial_appeal(features: Dict, metadata: Dict) -> float:
    """
    Score commercial/radio appeal (0-100)
    """
    score = 50.0
    
    # Tempo (100-130 BPM is most commercial)
    tempo = features["tempo"]
    if 100 <= tempo <= 130:
        score += 25
    elif 90 <= tempo <= 140:
        score += 15
    
    # Duration (3-4 minutes is ideal for radio)
    duration = features["duration"]
    if 180 <= duration <= 240:
        score += 25
    elif 150 <= duration <= 270:
        score += 15
    
    return min(100, max(0, score))


def calculate_innovation(features: Dict) -> float:
    """
    Score innovation and uniqueness (0-100)
    """
    score = 60.0  # Assume moderate innovation
    
    # Unusual tempo = more innovative
    tempo = features["tempo"]
    if tempo < 80 or tempo > 150:
        score += 15
    
    # Higher harmonic complexity = more innovative
    if features["harmonic_ratio"] > 0.6:
        score += 10
    
    # Varied dynamics = more innovative
    if features["rms_std"] > 0.1:
        score += 15
    
    return min(100, max(0, score))


def calculate_emotional_impact(features: Dict) -> float:
    """
    Score emotional impact (0-100)
    """
    score = 50.0
    
    # Energy (RMS)
    if features["rms_mean"] > 0.15:
        score += 20
    
    # Dynamic variation (emotional dynamics)
    if features["rms_std"] > 0.05:
        score += 20
    
    # Harmonic richness
    if features["harmonic_ratio"] > 0.5:
        score += 10
    
    return min(100, max(0, score))


def calculate_radio_readiness(features: Dict, metadata: Dict) -> float:
    """
    Score radio readiness (0-100)
    """
    score = 50.0
    
    # Duration (radio wants 2:30-4:00)
    duration = features["duration"]
    if 150 <= duration <= 240:
        score += 30
    elif 120 <= duration <= 270:
        score += 15
    
    # Loudness (radio standard is -14 LUFS)
    loudness_diff = abs(features["loudness"] - (-14.0))
    if loudness_diff < 2:
        score += 20
    elif loudness_diff < 4:
        score += 10
    
    return min(100, max(0, score))


def generate_insights(category_scores: Dict, features: Dict) -> List[str]:
    """
    Generate human-readable insights
    """
    insights = []
    
    # Overall assessment
    overall = sum(category_scores.values()) / len(category_scores)
    if overall >= 85:
        insights.append("🏆 Grammy-worthy production quality!")
    elif overall >= 70:
        insights.append("⭐ Strong hit potential detected")
    elif overall >= 60:
        insights.append("📻 Radio-ready with some polish")
    else:
        insights.append("🎵 Good foundation, needs refinement")
    
    # Specific strengths
    best_category = max(category_scores, key=category_scores.get)
    insights.append(f"✨ Strongest in: {best_category.replace('_', ' ').title()}")
    
    # Production insights
    if features["loudness"] < -16:
        insights.append("🔊 Track is quieter than commercial standards")
    elif features["loudness"] > -10:
        insights.append("⚠️ Track may be over-compressed")
    
    # Tempo insights
    tempo = features["tempo"]
    if tempo > 140:
        insights.append("⚡ High-energy tempo great for clubs/festivals")
    elif tempo < 90:
        insights.append("🌙 Slower tempo perfect for emotional moments")
    
    return insights


def generate_recommendations(category_scores: Dict, features: Dict) -> List[str]:
    """
    Generate actionable recommendations
    """
    recommendations = []
    
    # Identify weakest areas
    weak_categories = {k: v for k, v in category_scores.items() if v < 70}
    
    if "production_quality" in weak_categories:
        if abs(features["loudness"] - (-14)) > 3:
            recommendations.append("🎛️ Adjust mastering to target -14 LUFS")
        if features["dynamic_range"] < 6:
            recommendations.append("🎚️ Reduce compression to preserve dynamics")
    
    if "commercial_appeal" in weak_categories:
        if features["duration"] < 150:
            recommendations.append("⏱️ Consider extending to 2:30-3:30 for radio")
        elif features["duration"] > 270:
            recommendations.append("✂️ Trim to under 4 minutes for radio play")
    
    if "radio_readiness" in weak_categories:
        recommendations.append("📻 Optimize for streaming loudness standards")
    
    if not recommendations:
        recommendations.append("🎉 Track is well-balanced and ready for release!")
    
    return recommendations


def analyze_trends(genre: str, features: Dict) -> Dict:
    """
    Analyze how track compares to current trends
    """
    try:
        # TODO: Integrate with Billboard/Spotify API for real trend data
        # For now, return simulated trend analysis
        
        # Genre-specific benchmarks
        genre_benchmarks = {
            "pop": {"tempo": 120, "loudness": -8, "duration": 195},
            "hip-hop": {"tempo": 140, "loudness": -6, "duration": 180},
            "edm": {"tempo": 128, "loudness": -7, "duration": 210},
            "rock": {"tempo": 125, "loudness": -10, "duration": 220},
        }
        
        benchmark = genre_benchmarks.get(genre.lower() if genre else "pop", genre_benchmarks["pop"])
        
        # Calculate similarity to trend
        tempo_diff = abs(features["tempo"] - benchmark["tempo"])
        loudness_diff = abs(features["loudness"] - benchmark["loudness"])
        
        trend_score = max(0, 100 - (tempo_diff * 2) - (loudness_diff * 3))
        
        viral_score = min(100, trend_score + np.random.randint(-10, 15))
        
        return {
            "viral_score": float(viral_score),
            "trend_alignment": float(trend_score),
            "genre_match": genre or "unknown",
            "trending_elements": ["catchy_hook", "modern_production"] if trend_score > 70 else ["unique_sound"]
        }
    
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        return {"viral_score": 50.0, "trend_alignment": 50.0}
