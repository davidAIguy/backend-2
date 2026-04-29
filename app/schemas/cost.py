from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class CostBase(BaseModel):
    call_id: str
    agent_id: Optional[str] = None


class CostCreate(CostBase):
    pass


class CostResponse(BaseModel):
    id: str
    call_id: str
    agent_id: Optional[str] = None
    twilio_call_cost: float = 0.0
    twilio_minutes: float = 0.0
    livekit_minutes: float = 0.0
    livekit_cost: float = 0.0
    llm_tokens_used: int = 0
    llm_cost: float = 0.0
    transcription_seconds: int = 0
    transcription_cost: float = 0.0
    tool_calls: int = 0
    tool_cost: float = 0.0
    total_cost: float = 0.0
    cost_breakdown: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


# Cost analytics
class CostSummary(BaseModel):
    total_cost: float
    total_calls: int
    total_duration: int  # in seconds
    avg_cost_per_call: float
    avg_duration: float
    
    # Breakdown
    twilio_cost: float
    livekit_cost: float
    llm_cost: float
    transcription_cost: float
    tool_cost: float


class CostByAgent(BaseModel):
    agent_id: str
    agent_name: str
    total_cost: float
    total_calls: int
    avg_cost_per_call: float


class CostByPeriod(BaseModel):
    period: str  # day, week, month
    period_start: datetime
    period_end: datetime
    total_cost: float
    total_calls: int
