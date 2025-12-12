"""
Score models for Grammy Meter
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class ScoreBase(BaseModel):
    track_id: str
    overall_score: float = Field(..., ge=0, le=100)
    production_quality: float = Field(..., ge=0, le=100)
    commercial_appeal: float = Field(..., ge=0, le=100)
    innovation: float = Field(..., ge=0, le=100)
    emotional_impact: float = Field(..., ge=0, le=100)
    radio_readiness: float = Field(..., ge=0, le=100)


class ScoreCreate(ScoreBase):
    viral_potential: Optional[float] = Field(None, ge=0, le=100)
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None


class ScoreResponse(ScoreBase):
    id: str
    viral_potential: Optional[float] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScoreInDB(ScoreResponse):
    pass


class ScoreComparison(BaseModel):
    """Compare track score with averages"""
    track_score: float
    genre_average: float
    platform_average: float
    percentile: float  # Where this track ranks (0-100)


class LeaderboardEntry(BaseModel):
    track_id: str
    title: str
    user_id: str
    username: Optional[str] = None
    overall_score: float
    genre: Optional[str] = None
    rank: int
    created_at: datetime
