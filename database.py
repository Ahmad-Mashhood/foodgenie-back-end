import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm_models import Base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://neondb_owner:npg_Sy4CHfe9xqus@ep-muddy-wind-ay6y4pb7.c-5.us-east-2.aws.neon.tech/neondb?ssl=require"
)

SYNC_DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL",
    "postgresql://neondb_owner:npg_Sy4CHfe9xqus@ep-muddy-wind-ay6y4pb7.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

# Async Engine for FastAPI
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync Engine for Migrations / Scripts
sync_engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def parse_object_id(id_str: str) -> str:
    """Pass-through helper for string IDs."""
    return str(id_str) if id_str else None

def serialize_doc(model_or_dict):
    """
    Helper function to serialize SQLAlchemy ORM objects or dicts
    into JSON-friendly dictionaries for FastAPI responses.
    """
    if model_or_dict is None:
        return None
    if isinstance(model_or_dict, list):
        return [serialize_doc(item) for item in model_or_dict]
    if hasattr(model_or_dict, "__table__"):
        res = {}
        for c in model_or_dict.__table__.columns:
            res[c.name] = getattr(model_or_dict, c.name)
        return res
    if isinstance(model_or_dict, dict):
        return model_or_dict
    return model_or_dict
