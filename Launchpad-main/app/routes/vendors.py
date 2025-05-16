from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from app import models, schemas
from app.schemas import VendorOut, VendorCreate, VendorUpdate
from app.auth import get_db, get_password_hash, verify_token
from app.models import Vendor, User
from app.dependencies import admin_only, vendor_only
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os 

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Use the token directly to determine permissions 
# instead of looking up the user in the database
async def get_current_user_from_token(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = verify_token(token, db)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user_id = int(payload.get("sub"))
        role = payload.get("role")
        
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        # Return both token data and user data for flexibility
        return {"user_id": user_id, "role": role, "token_data": payload}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/vendors", response_model=list[VendorOut])
async def all_vendors(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user_from_token)
):
    # Use the role from the token itself
    role = current_user.get("role")
    
    if role not in ["admin", "vendor"]:
        raise HTTPException(status_code=403, detail="Admin or vendor privileges required")
    
    vendors = db.query(models.Vendor).all()
    return vendors

@router.post("/register/vendor", response_model=VendorOut)
async def register_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    existing_vendor = db.query(Vendor).filter(Vendor.email == vendor.email).first()

    if existing_vendor:
        raise HTTPException(status_code=400, detail="Vendor already exists")
    
    hashed_pw = get_password_hash(vendor.password)

    new_vendor = Vendor(
        name=vendor.name,
        email=vendor.email,
        hashed_password=hashed_pw,
        phone=vendor.phone
    )

    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    return new_vendor