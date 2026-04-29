from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.tool import Tool
from app.schemas.tool import ToolCreate, ToolUpdate, ToolResponse, ToolExecute, ToolExecuteResult
from app.services.tool_service import ToolService

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool_data: ToolCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tool"""
    # Check if tool name already exists
    result = await db.execute(select(Tool).where(Tool.name == tool_data.name))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Tool with this name already exists"
        )
    
    tool = Tool(
        name=tool_data.name,
        description=tool_data.description,
        type=tool_data.type,
        config=tool_data.config,
        parameters=tool_data.parameters,
        mcp_server=tool_data.mcp_server,
        mcp_tools=tool_data.mcp_tools,
        is_active=tool_data.is_active
    )
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


@router.get("/", response_model=List[ToolResponse])
async def list_tools(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    tool_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all tools"""
    query = select(Tool)
    
    if is_active is not None:
        query = query.where(Tool.is_active == is_active)
    if tool_type:
        query = query.where(Tool.type == tool_type)
    
    query = query.offset(skip).limit(limit).order_by(Tool.created_at.desc())
    result = await db.execute(query)
    tools = result.scalars().all()
    return tools


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get tool by ID"""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return tool


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: str,
    tool_data: ToolUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a tool"""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    update_data = tool_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tool, key, value)
    
    tool.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(tool)
    return tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a tool"""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    await db.delete(tool)
    await db.commit()


@router.post("/execute", response_model=ToolExecuteResult)
async def execute_tool(
    tool_exec: ToolExecute,
    db: AsyncSession = Depends(get_db)
):
    """Execute a tool with given parameters"""
    # Get tool from database
    result = await db.execute(select(Tool).where(Tool.name == tool_exec.tool_name))
    tool = result.scalar_one_or_none()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    if not tool.is_active:
        raise HTTPException(status_code=400, detail="Tool is not active")
    
    # Execute tool using ToolService
    tool_service = ToolService()
    result = await tool_service.execute_tool(tool, tool_exec.parameters)
    
    # Update tool usage counter if successful
    if result.success:
        tool.total_calls = str(int(tool.total_calls) + 1)
        await db.commit()
    
    return result
