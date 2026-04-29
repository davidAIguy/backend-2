from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import Response, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from twilio.twiml.voice_response import VoiceResponse, Connect
import httpx
import json

from app.core.database import get_db
from app.core.config import get_settings
from app.services.twilio_service import TwilioService
from app.services.livekit_service import LiveKitService
from app.models.agent import Agent
from app.models.call import Call, CallStatus, CallDirection
from app.models.transcript import Transcript

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


@router.post("/twilio/call", response_class=PlainTextResponse)
async def twilio_inbound_call(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle inbound calls from Twilio.
    This webhook is called when someone calls your Twilio number.
    """
    # Get call parameters
    form_data = await request.form()
    from_number = form_data.get("From", "")
    to_number = form_data.get("To", "")
    
    # Find agent by phone number
    result = await db.execute(
        select(Agent).where(Agent.phone_number == to_number, Agent.is_active == True)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        # No agent found - play a message or redirect
        response = VoiceResponse()
        response.say("Thank you for calling. No agent is available at this time.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    # Create call record
    from datetime import datetime
    call_id = str(form_data.get("CallSid", "unknown"))
    
    # Check if call already exists
    existing = await db.execute(
        select(Call).where(Call.twilio_call_sid == call_id)
    )
    existing_call = existing.scalar_one_or_none()
    
    if not existing_call:
        call = Call(
            id=call_id if len(call_id) == 36 else str(form_data.get("CallSid", "")),
            twilio_call_sid=form_data.get("CallSid"),
            from_number=from_number,
            to_number=to_number,
            direction=CallDirection.INBOUND,
            agent_id=agent.id,
            status=CallStatus.RINGING,
            start_time=datetime.utcnow()
        )
        db.add(call)
        
        # Create transcript
        transcript = Transcript(
            call_id=call.id,
            agent_id=agent.id,
            started_at=datetime.utcnow()
        )
        db.add(transcript)
        
        await db.commit()
    
    # Generate TwiML to connect to LiveKit
    response = VoiceResponse()
    room_name = f"call-{call_id}"
    
    connect = Connect()
    connect.stream(
        url=f"{settings.LIVEKIT_URL}/room/{room_name}",
        name="voice-agent"
    )
    response.append(connect)
    
    return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/call-status")
async def twilio_call_status(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle call status callbacks from Twilio.
    Updates call status in the database.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    call_status = form_data.get("CallStatus", "")
    call_duration = form_data.get("CallDuration", "0")
    
    twilio_service = TwilioService()
    await twilio_service.handle_call_status_webhook(
        db=db,
        call_sid=call_sid,
        status=call_status
    )
    
    return {"status": "ok"}


@router.post("/twilio/recording")
async def twilio_recording(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle recording completed webhook from Twilio"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    recording_url = form_data.get("RecordingUrl", "")
    
    # Find call and update transcript with recording
    result = await db.execute(
        select(Call).where(Call.twilio_call_sid == call_sid)
    )
    call = result.scalar_one_or_none()
    
    if call:
        transcript_result = await db.execute(
            select(Transcript).where(Transcript.call_id == call.id)
        )
        transcript = transcript_result.scalar_one_or_none()
        
        if transcript:
            transcript.recording_url = recording_url
            await db.commit()
    
    return {"status": "ok"}


@router.post("/livekit/events")
async def livekit_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle events from LiveKit.
    Used for tracking call status and transcription.
    """
    body = await request.json()
    
    # Handle different event types
    event_type = body.get("event")
    
    if event_type == "room_started":
        room_name = body.get("room", {}).get("name", "")
        # Room started - call is active
        
    elif event_type == "room_finished":
        room_name = body.get("room", {}).get("name", "")
        # Room finished - call ended
        
        # Update call status
        result = await db.execute(
            select(Call).where(Call.livekit_room == room_name)
        )
        call = result.scalar_one_or_none()
        
        if call:
            call.status = CallStatus.COMPLETED
            await db.commit()
    
    elif event_type == "participant_joined":
        # A participant joined the room
        pass
    
    elif event_type == "participant_left":
        # A participant left the room
        pass
    
    elif event_type == "transcription":
        # Transcription data from LiveKit
        transcript_text = body.get("transcript", "")
        speaker_id = body.get("speakerId", "")
        room_name = body.get("room", {}).get("name", "")
        
        # Update transcript
        result = await db.execute(
            select(Call).where(Call.livekit_room == room_name)
        )
        call = result.scalar_one_or_none()
        
        if call:
            transcript_result = await db.execute(
                select(Transcript).where(Transcript.call_id == call.id)
            )
            transcript = transcript_result.scalar_one_or_none()
            
            if transcript:
                # Append to messages
                messages = transcript.messages or []
                messages.append({
                    "role": "user" if speaker_id != "agent" else "assistant",
                    "content": transcript_text,
                    "speaker_id": speaker_id,
                    "timestamp": body.get("timestamp")
                })
                transcript.messages = messages
                transcript.transcript_text = (transcript.transcript_text or "") + f"\n{speaker_id}: {transcript_text}"
                await db.commit()
    
    return {"status": "ok"}


@router.get("/livekit/room-token/{room_name}")
async def get_livekit_token(
    room_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a LiveKit token for accessing a room.
    This can be used for testing or admin purposes.
    """
    livekit_service = LiveKitService()
    
    # Find call by room name
    result = await db.execute(
        select(Call).where(Call.livekit_room == room_name)
    )
    call = result.scalar_one_or_none()
    
    if not call:
        return {"error": "Room not found"}
    
    # Get agent
    agent_result = await db.execute(
        select(Agent).where(Agent.id == call.agent_id)
    )
    agent = agent_result.scalar_one_or_none()
    
    if not agent:
        return {"error": "Agent not found"}
    
    # Generate participant token
    token = await livekit_service.generate_participant_token(
        identity="admin",
        name="Admin User",
        room_name=room_name
    )
    
    return {
        "token": token,
        "wsUrl": settings.LIVEKIT_URL,
        "roomName": room_name
    }
