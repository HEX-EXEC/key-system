# app/routes/blacklist.py
from fastapi import APIRouter, Depends, HTTPException  # Add APIRouter here
from sqlalchemy.ext.asyncio import AsyncSession
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.BlacklistResponse)
async def blacklist_key(blacklist: schemas.BlacklistCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if await crud.is_blacklisted(db, blacklist.key):
        raise HTTPException(status_code=400, detail="Key already blacklisted")
    return await crud.blacklist_key(db, blacklist)