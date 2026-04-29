from twilio.twiml.voice_response import VoiceResponse, Dial, Connect
from twilio.rest import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from app.core.config import get_settings
from app.models.agent import Agent
from app.models.call import Call, CallStatus, CallDirection
from app.models.transcript import Transcript

settings = get_settings()


class TwilioService:
    """Service for handling Twilio voice calls"""
    
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    async def create_inbound_call_webhook(self, from_number: str, to_number: str) -> str:
        """
        Generate TwiML response for inbound calls.
        This connects the call to LiveKit.
        """
        response = VoiceResponse()
        
        # Find agent by phone number
        # In production, you'd look this up from the database
        
        # For now, generate TwiML to connect to LiveKit
        # The actual connection happens through LiveKit's SIP trunk or phone number forwarding
        
        # Using Twilio's <Connect> verb to connect to LiveKit
        connect = Connect()
        room_url = f"{settings.LIVEKIT_URL}/room/{to_number.replace('+', '')}"
        connect.stream(url=room_url)
        response.append(connect)
        
        return str(response)
    
    async def make_outbound_call(
        self,
        db: AsyncSession,
        from_number: str,
        to_number: str,
        agent_id: str
    ) -> str:
        """Initiate an outbound call"""
        
        # Create call record
        call_id = str(uuid.uuid4())
        call = Call(
            id=call_id,
            from_number=from_number,
            to_number=to_number,
            direction=CallDirection.OUTBOUND,
            agent_id=agent_id,
            status=CallStatus.RINGING,
            twilio_call_sid=None  # Will be updated when Twilio responds
        )
        db.add(call)
        await db.commit()
        
        # Create transcript record
        transcript = Transcript(
            call_id=call_id,
            agent_id=agent_id,
            started_at=datetime.utcnow()
        )
        db.add(transcript)
        await db.commit()
        
        # Generate TwiML for the outbound call
        response = VoiceResponse()
        
        # Connect to LiveKit
        connect = Connect()
        room_name = f"outbound-{call_id}"
        connect.stream(url=f"{settings.LIVEKIT_URL}/room/{room_name}")
        response.append(connect)
        
        # Make the call via Twilio
        twilio_call = self.client.calls.create(
            to=to_number,
            from_=from_number,
            twiml=str(response),
            status_callback=f"{settings.APP_URL}/webhooks/twilio/call-status",
            status_callback_event=["initiated", "ringing", "answered", "completed"]
        )
        
        # Update call with Twilio SID
        call.twilio_call_sid = twilio_call.sid
        call.livekit_room = room_name
        await db.commit()
        
        return call_id
    
    async def handle_call_status_webhook(
        self,
        db: AsyncSession,
        call_sid: str,
        status: str
    ):
        """Handle call status updates from Twilio"""
        
        # Find call by Twilio SID
        result = await db.execute(
            select(Call).where(Call.twilio_call_sid == call_sid)
        )
        call = result.scalar_one_or_none()
        
        if not call:
            return
        
        # Map Twilio status to our status
        status_map = {
            "initiated": CallStatus.RINGING,
            "ringing": CallStatus.RINGING,
            "in-progress": CallStatus.IN_PROGRESS,
            "completed": CallStatus.COMPLETED,
            "failed": CallStatus.FAILED,
            "busy": CallStatus.BUSY,
            "no-answer": CallStatus.NO_ANSWER,
            "canceled": CallStatus.FAILED
        }
        
        new_status = status_map.get(status, CallStatus.FAILED)
        call.status = new_status
        
        if new_status == CallStatus.IN_PROGRESS and not call.start_time:
            call.start_time = datetime.utcnow()
        elif new_status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.NO_ANSWER, CallStatus.BUSY]:
            call.end_time = datetime.utcnow()
            if call.start_time:
                call.duration = int((call.end_time - call.start_time).total_seconds())
            
            # Update transcript end time
            transcript_result = await db.execute(
                select(Transcript).where(Transcript.call_id == call.id)
            )
            transcript = transcript_result.scalar_one_or_none()
            if transcript:
                transcript.ended_at = call.end_time
                transcript.duration = call.duration
        
        await db.commit()
    
    def get_call_details(self, call_sid: str) -> dict:
        """Get call details from Twilio"""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "direction": call.direction,
                "from": call.from_formatted,
                "to": call.to_formatted,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "price": call.price,
                "price_unit": call.price_unit
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_available_phone_numbers(self) -> list:
        """Get available phone numbers from Twilio (requires Twilio Flex or similar)"""
        try:
            incoming_phones = self.client.incoming_phone_numbers.list()
            return [
                {
                    "sid": phone.sid,
                    "phone_number": phone.phone_number,
                    "friendly_name": phone.friendly_name
                }
                for phone in incoming_phones
            ]
        except Exception as e:
            return []
