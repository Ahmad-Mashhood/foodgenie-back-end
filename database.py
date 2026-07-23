import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models import Base
import models.user
import models.vendor
import models.food
import models.order
import models.rider
import models.review
import models.user_preferences

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://neondb_owner:npg_Sy4CHfe9xqus@ep-muddy-wind-ay6y4pb7.c-5.us-east-2.aws.neon.tech/neondb?ssl=require"
)

SYNC_DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL",
    "postgresql://neondb_owner:npg_Sy4CHfe9xqus@ep-muddy-wind-ay6y4pb7.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

# Synchronous Engine & Session
engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Async Engine & Session for FastAPI
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

def init_sync_db():
    Base.metadata.create_all(bind=engine)

async def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_object_id(id_str: str):
    try:
        return int(id_str)
    except (ValueError, TypeError):
        return id_str

def serialize_doc(model_or_dict):
    """
    Helper function to convert SQLAlchemy ORM instances or list of models into dicts.
    """
    if model_or_dict is None:
        return None
    if isinstance(model_or_dict, list):
        return [serialize_doc(item) for item in model_or_dict]
    if hasattr(model_or_dict, "__table__"):
        res = {}
        for c in model_or_dict.__table__.columns:
            val = getattr(model_or_dict, c.name)
            if hasattr(val, "isoformat"):
                val = val.isoformat()
            res[c.name] = val
        return res
    if isinstance(model_or_dict, dict):
        return model_or_dict
    return model_or_dict
