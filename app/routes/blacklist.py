# app/routes/blacklist.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

@router.get("/")
def get_blacklist(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_blacklist(db)

@router.post("/", response_model=schemas.Blacklist)
def add_to_blacklist(blacklist: schemas.BlacklistCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.add_to_blacklist(db, blacklist)

@router.delete("/")
def remove_from_blacklist(blacklist: schemas.BlacklistDelete, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.remove_from_blacklist(db, blacklist)