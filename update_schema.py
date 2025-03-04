# update_schema.py
import asyncio
from sqlalchemy.sql import text  # Import text from sqlalchemy.sql
from app.database import engine

async def add_success_column():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE logs ADD COLUMN success BOOLEAN DEFAULT TRUE"))
    print("Column 'success' added to 'logs' table.")

asyncio.run(add_success_column())