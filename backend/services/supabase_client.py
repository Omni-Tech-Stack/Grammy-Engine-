"""
Supabase Client - Database and storage integration
"""
from supabase import create_client, Client
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Global client instance
supabase: Optional[Client] = None


def init_supabase() -> Client:
    """
    Initialize Supabase client
    """
    global supabase
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not configured")
        return None
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")
        return supabase
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
        raise


def get_supabase() -> Client:
    """
    Get Supabase client instance
    """
    global supabase
    
    if supabase is None:
        supabase = init_supabase()
    
    return supabase


async def upload_audio_file(file_data: bytes, filename: str, content_type: str = "audio/wav") -> str:
    """
    Upload audio file to Supabase Storage
    
    Args:
        file_data: Binary file data
        filename: File path in storage
        content_type: MIME type
    
    Returns:
        Public URL of uploaded file
    """
    try:
        client = get_supabase()
        
        if not client:
            logger.warning("Supabase not configured, returning local path")
            return f"/local/{filename}"
        
        # Upload to 'audio' bucket
        bucket_name = "audio"
        
        # Upload file
        response = client.storage.from_(bucket_name).upload(
            filename,
            file_data,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        
        # Get public URL
        public_url = client.storage.from_(bucket_name).get_public_url(filename)
        
        logger.info(f"File uploaded: {filename}")
        
        return public_url
    
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise


async def download_audio_file(filename: str) -> bytes:
    """
    Download audio file from Supabase Storage
    """
    try:
        client = get_supabase()
        
        if not client:
            raise ValueError("Supabase not configured")
        
        bucket_name = "audio"
        
        # Download file
        response = client.storage.from_(bucket_name).download(filename)
        
        logger.info(f"File downloaded: {filename}")
        
        return response
    
    except Exception as e:
        logger.error(f"File download failed: {e}")
        raise


async def delete_audio_file(filename: str) -> bool:
    """
    Delete audio file from Supabase Storage
    """
    try:
        client = get_supabase()
        
        if not client:
            raise ValueError("Supabase not configured")
        
        bucket_name = "audio"
        
        # Delete file
        client.storage.from_(bucket_name).remove([filename])
        
        logger.info(f"File deleted: {filename}")
        
        return True
    
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        return False


# Database schema reference
"""
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    tier VARCHAR(50) DEFAULT 'free',
    generation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tracks table
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    prompt TEXT,
    lyrics TEXT,
    genre VARCHAR(100),
    duration INTEGER,
    tempo INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    audio_url TEXT,
    mastered_url TEXT,
    vocal_url TEXT,
    stem_urls JSONB,
    grammy_score FLOAT,
    has_vocals BOOLEAN DEFAULT FALSE,
    type VARCHAR(50) DEFAULT 'instrumental',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    mastered_at TIMESTAMP
);

-- Grammy Scores table
CREATE TABLE grammy_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    track_id UUID REFERENCES tracks(id) ON DELETE CASCADE,
    overall_score FLOAT NOT NULL,
    production_quality FLOAT,
    commercial_appeal FLOAT,
    innovation FLOAT,
    emotional_impact FLOAT,
    radio_readiness FLOAT,
    viral_potential FLOAT,
    insights JSONB,
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Prompts table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    original_prompt TEXT NOT NULL,
    enhanced_prompt TEXT,
    genre VARCHAR(100),
    mood VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Trend Data table
CREATE TABLE trend_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data JSONB NOT NULL,
    analyzed_at TIMESTAMP DEFAULT NOW()
);

-- Storage bucket (create via Supabase dashboard or SQL)
-- Name: audio
-- Public: true (or false with signed URLs)
"""
