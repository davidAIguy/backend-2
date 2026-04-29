from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    call_id = Column(String(36), ForeignKey("calls.id"), nullable=False, unique=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=True)
    
    # Full transcript text
    transcript_text = Column(Text, nullable=True)
    
    # Structured messages (conversation turns)
    messages = Column(JSON, default=list)  # List of {role, content, timestamp, tool_calls}
    
    # Stats
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    agent_messages = Column(Integer, default=0)
    tool_calls = Column(Integer, default=0)
    
    # Audio URL (if recording enabled)
    recording_url = Column(String(500), nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Integer, default=0)  # in seconds
    
    # Cost tracking
    transcription_cost = Column(Float, default=0.0)
    llm_cost = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship("Call", back_populates="transcript")
    agent = relationship("Agent", back_populates="transcripts")
