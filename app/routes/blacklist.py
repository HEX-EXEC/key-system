from fastapi import APIRouter, Depends, HTTPException
from app import schemas, crud  # Absolute import
from app.auth import get_current_user  # Absolute import
from app.database import get_db  # Absolute import
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/")
def add_to_blacklist(blacklist: schemas.Blacklist, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if crud.is_key_blacklisted(db, blacklist.key):
        raise HTTPException(status_code=400, detail="Key already blacklisted")
    db_blacklist = crud.add_to_blacklist(db, blacklist.key, blacklist.reason)
    return {"key": blacklist.key, "reason": blacklist.reason}

@router.delete("/")
def remove_from_blacklist(blacklist: schemas.BlacklistRemove, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if not crud.is_key_blacklisted(db, blacklist.key):
        raise HTTPException(status_code=404, detail="Key not blacklisted")
    crud.remove_from_blacklist(db, blacklist.key)
    return {"message": "Key removed from blacklist"}