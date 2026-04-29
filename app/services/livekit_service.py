from livekit import api
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.config import get_settings
from app.models.agent import Agent
from app.models.call import Call, CallStatus, CallDirection
from app.models.transcript import Transcript

settings = get_settings()


class LiveKitService:
    """Service for handling LiveKit voice agents"""
    
    def __init__(self):
        self.livekit_api = api.LiveKitAPI(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
    
    async def create_room(self, room_name: str) -> dict:
        """Create a LiveKit room"""
        try:
            room_service = api.RoomServiceClient(
                settings.LIVEKIT_URL,
                settings.LIVEKIT_API_KEY,
                settings.LIVEKIT_API_SECRET
            )
            
            room = await room_service.create_room(
                api.CreateRoomRequest(name=room_name)
            )
            
            return {
                "success": True,
                "room_name": room.name,
                "room_id": room.sid
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_agent_token(
        self,
        agent_id: str,
        agent_name: str,
        room_name: str
    ) -> str:
        """Generate access token for the AI agent"""
        
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
        
        token.with_identity(f"agent-{agent_id}")
        token.with_name(agent_name)
        
        # Grant agent permissions
        grant = api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        )
        
        token.with_grants(grant)
        
        return token.to_jwt()
    
    async def generate_participant_token(
        self,
        identity: str,
        name: str,
        room_name: str
    ) -> str:
        """Generate access token for a participant"""
        
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
        
        token.with_identity(identity)
        token.with_name(name)
        
        grant = api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        )
        
        token.with_grants(grant)
        
        return token.to_jwt()
    
    async def get_room_info(self, room_name: str) -> Optional[dict]:
        """Get information about a room"""
        try:
            room_service = api.RoomServiceClient(
                settings.LIVEKIT_URL,
                settings.LIVEKIT_API_KEY,
                settings.LIVEKIT_API_SECRET
            )
            
            room = await room_service.get_room(
                api.RoomName(room_name)
            )
            
            participants = await room_service.list_participants(
                api.RoomName(room_name)
            )
            
            return {
                "name": room.name,
                "sid": room.sid,
                "status": room.status,
                "participant_count": len(participants.participants),
                "created_at": room.creation_time
            }
        except Exception as e:
            return None
    
    async def end_room(self, room_name: str) -> bool:
        """End a LiveKit room"""
        try:
            room_service = api.RoomServiceClient(
                settings.LIVEKIT_URL,
                settings.LIVEKIT_API_KEY,
                settings.LIVEKIT_API_SECRET
            )
            
            await room_service.delete_room(api.RoomName(room_name))
            return True
        except Exception:
            return False
    
    async def start_call(
        self,
        db: AsyncSession,
        call_id: str,
        room_name: str
    ) -> bool:
        """Initialize a call session with LiveKit"""
        
        # Update call with LiveKit room
        result = await db.execute(select(Call).where(Call.id == call_id))
        call = result.scalar_one_or_none()
        
        if not call:
            return False
        
        call.livekit_room = room_name
        call.status = CallStatus.IN_PROGRESS
        call.start_time = datetime.utcnow()
        
        await db.commit()
        return True
    
    async def end_call(
        self,
        db: AsyncSession,
        call_id: str
    ) -> bool:
        """End a call session"""
        
        result = await db.execute(select(Call).where(Call.id == call_id))
        call = result.scalar_one_or_none()
        
        if not call:
            return False
        
        call.status = CallStatus.COMPLETED
        call.end_time = datetime.utcnow()
        
        if call.start_time:
            call.duration = int((call.end_time - call.start_time).total_seconds())
        
        await db.commit()
        return True
    
    def get_agent_config(self, agent: Agent) -> Dict[str, Any]:
        """Get configuration for the LiveKit agent"""
        return {
            "name": agent.name,
            "system_prompt": agent.system_prompt,
            "voice": agent.voice,
            "llm_model": agent.llm_model,
            "tools": agent.tools or []
        }
