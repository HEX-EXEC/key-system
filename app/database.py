# app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Use Render's DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgres://"):]

# Explicitly create an async engine with asyncpg, disable fallback to sync drivers
engine = create_async_engine(DATABASE_URL, async_fallback=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session