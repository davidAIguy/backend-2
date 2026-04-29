from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.transcript import Transcript
from app.schemas.transcript import TranscriptResponse, TranscriptUpdate

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.get("/call/{call_id}", response_model=TranscriptResponse)
async def get_transcript_by_call(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get transcript by call ID"""
    result = await db.execute(
        select(Transcript).where(Transcript.call_id == call_id)
    )
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return transcript


@router.get("/{transcript_id}", response_model=TranscriptResponse)
async def get_transcript(
    transcript_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get transcript by ID"""
    result = await db.execute(
        select(Transcript).where(Transcript.id == transcript_id)
    )
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return transcript


@router.put("/{transcript_id}", response_model=TranscriptResponse)
async def update_transcript(
    transcript_id: str,
    transcript_data: TranscriptUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update transcript"""
    result = await db.execute(
        select(Transcript).where(Transcript.id == transcript_id)
    )
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    update_data = transcript_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transcript, key, value)
    
    await db.commit()
    await db.refresh(transcript)
    return transcript


@router.get("/agent/{agent_id}", response_model=List[TranscriptResponse])
async def get_transcripts_by_agent(
    agent_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get transcripts by agent ID"""
    query = select(Transcript).where(
        Transcript.agent_id == agent_id
    ).order_by(Transcript.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    transcripts = result.scalars().all()
    return transcripts


@router.get("/{transcript_id}/messages")
async def get_transcript_messages(
    transcript_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get transcript messages"""
    result = await db.execute(
        select(Transcript).where(Transcript.id == transcript_id)
    )
    transcript = result.scalar_one_or_none()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return {
        "transcript_id": transcript.id,
        "messages": transcript.messages or [],
        "stats": {
            "total_messages": transcript.total_messages,
            "user_messages": transcript.user_messages,
            "agent_messages": transcript.agent_messages,
            "tool_calls": transcript.tool_calls
        }
    }
