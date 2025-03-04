import asyncio
from app.crud import create_user
from app.schemas import UserCreate
from app.database import get_db

async def add_admin():
    async for db in get_db():
        await create_user(db, UserCreate(username="admin", password="securepassword123", role="admin"))
        break

asyncio.run(add_admin())