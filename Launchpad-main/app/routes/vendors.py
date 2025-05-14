from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_db, get_current_user


router = APIRouter()


@router.get("/vendors", response_model=list[schemas.VendorOut])
async def all_vendors(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    
    vendors = db.query(models.Vendor).all()