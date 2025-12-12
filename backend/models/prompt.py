"""
Prompt models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PromptBase(BaseModel):
    original_prompt: str = Field(..., min_length=10, max_length=1000)
    enhanced_prompt: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None


class PromptCreate(PromptBase):
    user_id: str


class PromptResponse(PromptBase):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PromptInDB(PromptResponse):
    pass
