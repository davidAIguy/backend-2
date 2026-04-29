from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ToolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: str = "function"  # function, mcp, webhook, api
    config: Dict[str, Any] = {}
    parameters: Dict[str, Any] = {}
    mcp_server: Optional[str] = None
    mcp_tools: List[str] = []
    is_active: bool = True


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    mcp_server: Optional[str] = None
    mcp_tools: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ToolResponse(ToolBase):
    id: str
    total_calls: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ToolExecute(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}


class ToolExecuteResult(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
