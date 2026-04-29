from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageItem(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    tool_calls: Optional[List[Dict[str, Any]]] = None


class TranscriptBase(BaseModel):
    call_id: str
    agent_id: Optional[str] = None


class TranscriptCreate(TranscriptBase):
    pass


class TranscriptResponse(BaseModel):
    id: str
    call_id: str
    agent_id: Optional[str] = None
    transcript_text: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    total_messages: int = 0
    user_messages: int = 0
    agent_messages: int = 0
    tool_calls: int = 0
    recording_url: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: int = 0
    transcription_cost: float = 0.0
    llm_cost: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True


class TranscriptUpdate(BaseModel):
    transcript_text: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    recording_url: Optional[str] = None
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    transcription_cost: Optional[float] = None
    llm_cost: Optional[float] = None
