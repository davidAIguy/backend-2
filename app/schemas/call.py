from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.call import CallStatus, CallDirection


class CallBase(BaseModel):
    from_number: str = Field(..., min_length=1)
    to_number: str = Field(..., min_length=1)
    direction: CallDirection


class CallCreate(CallBase):
    agent_id: Optional[str] = None


class CallResponse(CallBase):
    id: str
    twilio_call_sid: Optional[str] = None
    livekit_room: Optional[str] = None
    agent_id: Optional[str] = None
    status: CallStatus
    duration: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class CallUpdate(BaseModel):
    status: Optional[CallStatus] = None
    duration: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    cost: Optional[float] = None


class CallWithTranscript(CallResponse):
    transcript_text: Optional[str] = None
    total_messages: int = 0


# Pagination
class PaginatedCalls(BaseModel):
    items: List[CallResponse]
    total: int
    page: int
    page_size: int
    pages: int
