from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database (Supabase)
    DATABASE_URL: str = "postgresql://user:password@host:6543/postgres"
    
    # Supabase direct connection
    SUPABASE_DB_HOST: str = ""
    SUPABASE_DB_PORT: str = "6543"
    SUPABASE_DB_NAME: str = "postgres"
    SUPABASE_DB_USER: str = ""
    SUPABASE_DB_PASSWORD: str = ""
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # LiveKit
    LIVEKIT_URL: str = ""
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # App
    APP_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
