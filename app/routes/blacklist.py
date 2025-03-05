# app/routes/blacklist.py
from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, crud
from app.auth import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session  # Use synchronous Session

router = APIRouter()

@router.post("/", response_model=schemas.Blacklist)
def add_to_blacklist(blacklist: schemas.BlacklistCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_key = crud.get_key(db, blacklist.key)
    if not db_key:
        raise HTTPException(status_code=404, detail="Key not found")
    if crud.is_key_blacklisted(db, blacklist.key):
        raise HTTPException(status_code=400, detail="Key is already blacklisted")
    return crud.add_to_blacklist(db, blacklist.key, blacklist.reason)

@router.delete("/", response_model=dict)  # Return a simple dict for the response
def remove_from_blacklist(blacklist: schemas.BlacklistCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if not crud.is_key_blacklisted(db, blacklist.key):
        raise HTTPException(status_code=404, detail="Key not found in blacklist")
    crud.remove_from_blacklist(db, blacklist.key)
    return {"message": "Key removed from blacklist"}