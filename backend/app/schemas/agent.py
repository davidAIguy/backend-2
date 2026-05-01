from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Agent Schemas
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: str = Field(..., min_length=1)
    voice: str = "en-US-Neural2-Female"
    llm_model: str = "gpt-4-turbo-preview"
    tools: List[Dict[str, Any]] = []
    is_active: bool = True
    phone_number: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    voice: Optional[str] = None
    llm_model: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    phone_number: Optional[str] = None


class AgentResponse(AgentBase):
    id: str
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentWithStats(AgentResponse):
    total_calls: int = 0
    total_cost: float = 0.0
