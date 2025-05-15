from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from app import models, schemas
from app.schemas import VendorOut, VendorCreate, VendorUpdate
from app.auth import get_db, get_password_hash
from app.models import Vendor, User
from app.dependencies import admin_only, vendor_only
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os 

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")



router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def decode_jwt(token: str):
    print(f"toekn :::::: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        #print(f"ROLE : {role} --- USER ID : {user_id}")
        if user_id is None or role is None:
            raise HTTPException(status_code=403, detail="Invalid token payload")
        return {"user_id": int(user_id), "role": role}
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials----")

def get_current_user(token: str = Security(oauth2_scheme)):
    return decode_jwt(token)

def get_role(current_user: dict = Depends(get_current_user)):
    return current_user.get("role")

def admin_or_vendor_required(role: str = Depends(get_role)):
    if role not in ["admin", "vendor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return role

@router.get("/vendors", response_model=list[VendorOut])
async def all_vendors(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    payload = decode_jwt(current_user)
    role = payload.get("role")
    if role not in ["admin", "vendor"]:
        raise HTTPException(status_code=403, detail="admin/vendor privilege required")
    
    vendors = db.query(models.Vendor).all()
    print(vendors)

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

# @router.get("/vendors/{vendor_id}", response_model=schemas.VendorOut)
# async def get_vendor(vendor_id:int, db: Session = Depends(get_db))