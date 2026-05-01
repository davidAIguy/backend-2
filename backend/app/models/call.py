from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base


class CallStatus(str, enum.Enum):
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"


class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Call(Base):
    __tablename__ = "calls"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Call identification
    twilio_call_sid = Column(String(100), unique=True, nullable=True)
    livekit_room = Column(String(100), nullable=True)
    
    # Relationships
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=True)
    
    # Phone numbers
    from_number = Column(String(20), nullable=False)
    to_number = Column(String(20), nullable=False)
    
    # Direction and status
    direction = Column(Enum(CallDirection), nullable=False)
    status = Column(Enum(CallStatus), default=CallStatus.RINGING)
    
    # Duration in seconds
    duration = Column(Integer, default=0)
    
    # Timestamps
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Cost tracking
    cost = Column(Float, default=0.0)
    
    # Relationships
    agent = relationship("Agent", back_populates="calls")
    transcript = relationship("Transcript", back_populates="call", uselist=False)
    costs = relationship("Cost", back_populates="call")
