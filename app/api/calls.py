from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.call import Call, CallStatus, CallDirection
from app.models.transcript import Transcript
from app.schemas.call import CallResponse, CallUpdate, CallWithTranscript, PaginatedCalls

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("/", response_model=PaginatedCalls)
async def list_calls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    agent_id: Optional[str] = None,
    status: Optional[CallStatus] = None,
    direction: Optional[CallDirection] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all calls with pagination"""
    query = select(Call)
    
    if agent_id:
        query = query.where(Call.agent_id == agent_id)
    if status:
        query = query.where(Call.status == status)
    if direction:
        query = query.where(Call.direction == direction)
    
    # Count total
    count_query = select(func.count(Call.id))
    if agent_id:
        count_query = count_query.where(Call.agent_id == agent_id)
    if status:
        count_query = count_query.where(Call.status == status)
    if direction:
        count_query = count_query.where(Call.direction == direction)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Call.created_at.desc())
    result = await db.execute(query)
    calls = result.scalars().all()
    
    pages = (total + page_size - 1) // page_size
    
    return PaginatedCalls(
        items=calls,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get call by ID"""
    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return call


@router.get("/{call_id}/full", response_model=CallWithTranscript)
async def get_call_with_transcript(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get call with transcript"""
    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Get transcript
    transcript_result = await db.execute(
        select(Transcript).where(Transcript.call_id == call_id)
    )
    transcript = transcript_result.scalar_one_or_none()
    
    return CallWithTranscript(
        id=call.id,
        twilio_call_sid=call.twilio_call_sid,
        livekit_room=call.livekit_room,
        agent_id=call.agent_id,
        from_number=call.from_number,
        to_number=call.to_number,
        direction=call.direction,
        status=call.status,
        duration=call.duration,
        start_time=call.start_time,
        end_time=call.end_time,
        cost=call.cost,
        created_at=call.created_at,
        transcript_text=transcript.transcript_text if transcript else None,
        total_messages=transcript.total_messages if transcript else 0
    )


@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str,
    call_data: CallUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a call"""
    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    update_data = call_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(call, key, value)
    
    await db.commit()
    await db.refresh(call)
    return call


@router.post("/{call_id}/status", response_model=CallResponse)
async def update_call_status(
    call_id: str,
    status: CallStatus,
    db: AsyncSession = Depends(get_db)
):
    """Update call status"""
    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call.status = status
    
    if status == CallStatus.IN_PROGRESS and not call.start_time:
        call.start_time = datetime.utcnow()
    elif status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.NO_ANSWER, CallStatus.BUSY]:
        call.end_time = datetime.utcnow()
        if call.start_time:
            call.duration = int((call.end_time - call.start_time).total_seconds())
    
    await db.commit()
    await db.refresh(call)
    return call


@router.get("/phone/{phone_number}", response_model=List[CallResponse])
async def get_calls_by_phone(
    phone_number: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get calls by phone number (as from or to)"""
    query = select(Call).where(
        (Call.from_number == phone_number) | (Call.to_number == phone_number)
    ).order_by(Call.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    calls = result.scalars().all()
    return calls
