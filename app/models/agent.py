from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Agent configuration
    system_prompt = Column(Text, nullable=False)
    voice = Column(String(50), default="en-US-Neural2-Female")  # Default voice
    llm_model = Column(String(100), default="gpt-4-turbo-preview")
    
    # Phone number assignment
    phone_number = Column(String(20), nullable=True, unique=True)
    
    # Agent capabilities
    tools = Column(JSON, default=list)  # List of tool configurations
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    calls = relationship("Call", back_populates="agent")
    transcripts = relationship("Transcript", back_populates="agent")
    costs = relationship("Cost", back_populates="agent")
