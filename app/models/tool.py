from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from datetime import datetime
import uuid
from app.core.database import Base


class Tool(Base):
    __tablename__ = "tools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tool identification
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Tool type
    type = Column(String(50), default="function")  # function, mcp, webhook, api
    
    # Tool configuration
    config = Column(JSON, default=dict)  # {endpoint, method, headers, schema, etc}
    
    # Schema for function calling
    parameters = Column(JSON, default=dict)  # OpenAI function schema
    
    # MCP server connection (if applicable)
    mcp_server = Column(String(200), nullable=True)  # MCP server URL
    mcp_tools = Column(JSON, default=list)  # List of available tools from MCP
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    total_calls = Column(String(20), default="0")  # Stored as string to handle large numbers
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Example tool configurations
DEFAULT_TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "type": "function",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "search_database",
        "description": "Search records in the database",
        "type": "function",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "table": {"type": "string", "description": "Table to search"}
            },
            "required": ["query"]
        }
    }
]
