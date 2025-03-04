import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Use local PostgreSQL by default, override with DATABASE_URL for Heroku
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://keyuser:keypass123@localhost:5432/keydb")
# Replace 'postgres://' with 'postgresql+asyncpg://' for asyncpg compatibility (needed for Heroku)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgres://"):]

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session