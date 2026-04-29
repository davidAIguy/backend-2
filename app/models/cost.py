from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Cost(Base):
    __tablename__ = "costs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    call_id = Column(String(36), ForeignKey("calls.id"), nullable=False, unique=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=True)
    
    # Twilio costs
    twilio_call_cost = Column(Float, default=0.0)  # Per minute rate
    twilio_minutes = Column(Float, default=0.0)
    
    # LiveKit costs
    livekit_minutes = Column(Float, default=0.0)
    livekit_cost = Column(Float, default=0.0)  # Egress/ingress costs
    
    # AI/LLM costs
    llm_tokens_used = Column(Integer, default=0)
    llm_cost = Column(Float, default=0.0)
    
    # Transcription costs
    transcription_seconds = Column(Integer, default=0)
    transcription_cost = Column(Float, default=0.0)
    
    # Tool usage costs (if using external APIs)
    tool_calls = Column(Integer, default=0)
    tool_cost = Column(Float, default=0.0)
    
    # Total
    total_cost = Column(Float, default=0.0)
    
    # Breakdown JSON for detailed analytics
    cost_breakdown = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship("Call", back_populates="costs")
    agent = relationship("Agent", back_populates="costs")


# Pricing constants (can be moved to config)
TWILIO_VOICE_COST_PER_MINUTE = 0.008  # ~$0.50/month for small usage
LIVEKIT_COST_PER_MINUTE = 0.004  # Approximate, check LiveKit pricing
OPENAI_WHISPER_COST_PER_MINUTE = 0.006  # Whisper API pricing
OPENAI_GPT4_COST_PER_1K_TOKENS = 0.01  # Input tokens
