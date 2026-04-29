from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.cost import Cost
from app.models.call import Call
from app.models.agent import Agent
from app.schemas.cost import CostResponse, CostSummary, CostByAgent, CostByPeriod

router = APIRouter(prefix="/costs", tags=["costs"])


@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    agent_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get overall cost summary"""
    query = select(Cost)
    call_query = select(Call)
    
    if agent_id:
        query = query.where(Cost.agent_id == agent_id)
        call_query = call_query.where(Call.agent_id == agent_id)
    
    if start_date:
        query = query.where(Cost.created_at >= start_date)
        call_query = call_query.where(Call.created_at >= start_date)
    
    if end_date:
        query = query.where(Cost.created_at <= end_date)
        call_query = call_query.where(Call.created_at <= end_date)
    
    result = await db.execute(query)
    costs = result.scalars().all()
    
    # Get call stats
    calls_result = await db.execute(call_query)
    calls = calls_result.scalars().all()
    
    total_calls = len(calls)
    total_duration = sum(c.duration for c in calls) if calls else 0
    total_cost = sum(c.total_cost for c in costs) if costs else 0.0
    
    twilio_cost = sum(c.twilio_call_cost for c in costs) if costs else 0.0
    livekit_cost = sum(c.livekit_cost for c in costs) if costs else 0.0
    llm_cost = sum(c.llm_cost for c in costs) if costs else 0.0
    transcription_cost = sum(c.transcription_cost for c in costs) if costs else 0.0
    tool_cost = sum(c.tool_cost for c in costs) if costs else 0.0
    
    return CostSummary(
        total_cost=total_cost,
        total_calls=total_calls,
        total_duration=total_duration,
        avg_cost_per_call=total_cost / total_calls if total_calls > 0 else 0.0,
        avg_duration=total_duration / total_calls if total_calls > 0 else 0.0,
        twilio_cost=twilio_cost,
        livekit_cost=livekit_cost,
        llm_cost=llm_cost,
        transcription_cost=transcription_cost,
        tool_cost=tool_cost
    )


@router.get("/by-agent", response_model=List[CostByAgent])
async def get_costs_by_agent(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get costs grouped by agent"""
    query = select(
        Cost.agent_id,
        func.sum(Cost.total_cost).label("total_cost"),
        func.count(Cost.id).label("total_calls")
    ).group_by(Cost.agent_id)
    
    if start_date:
        query = query.where(Cost.created_at >= start_date)
    if end_date:
        query = query.where(Cost.created_at <= end_date)
    
    result = await db.execute(query)
    cost_groups = result.all()
    
    costs_by_agent = []
    for cost_group in cost_groups:
        if cost_group.agent_id:
            agent_result = await db.execute(
                select(Agent.name).where(Agent.id == cost_group.agent_id)
            )
            agent_name = agent_result.scalar() or "Unknown"
            
            costs_by_agent.append(CostByAgent(
                agent_id=cost_group.agent_id,
                agent_name=agent_name,
                total_cost=float(cost_group.total_cost or 0),
                total_calls=cost_group.total_calls or 0,
                avg_cost_per_call=float(cost_group.total_cost or 0) / cost_group.total_calls if cost_group.total_calls > 0 else 0.0
            ))
    
    return costs_by_agent


@router.get("/by-period", response_model=List[CostByPeriod])
async def get_costs_by_period(
    period: str = Query("day", regex="^(day|week|month)$"),
    agent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get costs grouped by period (day, week, or month)"""
    now = datetime.utcnow()
    
    if period == "day":
        periods = [(now - timedelta(days=i)).date() for i in range(30)]
    elif period == "week":
        periods = [(now - timedelta(weeks=i)).date() for i in range(12)]
    else:  # month
        periods = [(now.replace(day=1) - timedelta(days=30*i)).date().replace(day=1) for i in range(12)]
    
    costs_by_period = []
    
    for period_date in periods[:10]:  # Limit to last 10 periods
        if period == "day":
            start = datetime.combine(period_date, datetime.min.time())
            end = datetime.combine(period_date, datetime.max.time())
        elif period == "week":
            start = period_date - timedelta(days=period_date.weekday())
            start = datetime.combine(start, datetime.min.time())
            end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        else:
            start = datetime.combine(period_date, datetime.min.time())
            next_month = period_date.replace(day=28) + timedelta(days=4)
            end = next_month.replace(day=1) - timedelta(seconds=1)
        
        query = select(func.sum(Cost.total_cost), func.count(Cost.id)).where(
            Cost.created_at >= start,
            Cost.created_at <= end
        )
        
        if agent_id:
            query = query.where(Cost.agent_id == agent_id)
        
        result = await db.execute(query)
        cost_data = result.one()
        
        costs_by_period.append(CostByPeriod(
            period=period,
            period_start=start,
            period_end=end,
            total_cost=float(cost_data[0] or 0),
            total_calls=cost_data[1] or 0
        ))
    
    return costs_by_period


@router.get("/call/{call_id}", response_model=CostResponse)
async def get_call_cost(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get cost for a specific call"""
    result = await db.execute(
        select(Cost).where(Cost.call_id == call_id)
    )
    cost = result.scalar_one_or_none()
    
    if not cost:
        # Return zero cost if not found
        return CostResponse(
            id="",
            call_id=call_id,
            total_cost=0.0
        )
    
    return cost
