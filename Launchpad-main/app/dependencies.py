# Module: app/dependencies.py
#shared dependencies such as getdb and token_validation
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app import models, db
#from app.auth import verify_token
from fastapi.security import OAuth2PasswordBearer
import os
from app.security_utils import verify_token
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Dependency to get DB session
def get_db():
    database = db.SessionLocal()
    try:
        yield database
    finally:
        database.close()

# Get current user from JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)


# Role-based access checks
def admin_only(user: models.User = Depends(get_current_user)):
    print("DEBUG - User Role:", user.role)
    if user.role != "admin":
        print("User")
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def vendor_only(user: models.User = Depends(get_current_user)):
    if user.role != "vendor":
        raise HTTPException(status_code=403, detail="Vendor access required")
    return user

