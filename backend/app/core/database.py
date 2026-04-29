from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()


def get_database_url() -> str | None:
    """Get database URL with async driver for SQLAlchemy async support"""
    # Check Supabase direct connection first
    if settings.SUPABASE_DB_HOST and settings.SUPABASE_DB_USER:
        # Use Supabase direct connection with pooling
        return f"postgresql+asyncpg://{settings.SUPABASE_DB_USER}:{settings.SUPABASE_DB_PASSWORD}@{settings.SUPABASE_DB_HOST}:{settings.SUPABASE_DB_PORT}/{settings.SUPABASE_DB_NAME}"
    
    # Check DATABASE_URL
    db_url = settings.DATABASE_URL
    if db_url and "localhost" not in db_url and "user:password" not in db_url:
        # Ensure DATABASE_URL uses asyncpg driver
        if db_url.startswith("postgresql://"):
            return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql+asyncpg://"):
            return db_url
    
    return None


# Lazy engine initialization
_engine = None
_async_session_maker = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = get_database_url()
        if db_url is None:
            return None
        _engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
    return _engine


def get_session_maker():
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_engine()
        if engine is None:
            return None
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _async_session_maker


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    session_maker = get_session_maker()
    if session_maker is None:
        raise RuntimeError("Database not configured. Please set SUPABASE_DB_* environment variables.")
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    engine = get_engine()
    if engine is None:
        print("Database not configured - skipping table creation")
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
