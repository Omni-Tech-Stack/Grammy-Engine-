"""
Track models
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class TrackStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    ADDING_VOCALS = "adding_vocals"
    MASTERING = "mastering"
    COMPLETED = "completed"
    FAILED = "failed"


class TrackType(str, Enum):
    INSTRUMENTAL = "instrumental"
    VOCAL = "vocal"
    ACAPELLA = "acapella"


class TrackBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    prompt: Optional[str] = None
    lyrics: Optional[str] = None
    genre: Optional[str] = None
    duration: Optional[int] = None
    tempo: Optional[int] = None


class TrackCreate(TrackBase):
    user_id: str
    type: TrackType = TrackType.INSTRUMENTAL


class TrackUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TrackStatus] = None
    audio_url: Optional[str] = None
    mastered_url: Optional[str] = None
    vocal_url: Optional[str] = None
    stem_urls: Optional[Dict[str, str]] = None
    grammy_score: Optional[float] = None


class TrackResponse(TrackBase):
    id: str
    user_id: str
    status: TrackStatus
    audio_url: Optional[str] = None
    mastered_url: Optional[str] = None
    vocal_url: Optional[str] = None
    stem_urls: Optional[Dict[str, str]] = None
    grammy_score: Optional[float] = None
    has_vocals: bool = False
    type: TrackType
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    mastered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TrackInDB(TrackResponse):
    pass


class TrackWithScore(TrackResponse):
    score_details: Optional[Dict] = None
