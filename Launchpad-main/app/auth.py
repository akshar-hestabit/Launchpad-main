from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import schemas, models, db
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import status
from typing import Optional
import uuid
from app.dependencies import get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()

#OAuth2 scheme for token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    database = db.SessionLocal()
    try:
        yield database
    finally:
        database.close()

@router.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, database: Session = Depends(get_db)):
    existing = database.query(models.User).filter(models.User.username == user.username).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role
    )

    database.add(new_user)
    database.commit()
    database.refresh(new_user)
    return new_user

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, db: Session):
    print("verify_token called")  
    try:
        # Check if token is blacklisted
        blacklisted = db.query(models.TokenBlacklist).filter(models.TokenBlacklist.token == token).first()
        if blacklisted:
            print("Token is blacklisted")  
            return None

        print("Decoding token...")  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded payload:", payload)  

        return payload  
    except JWTError as e:
        return None


@router.post("/login", response_model=schemas.Token)
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user.id,
    }

@router.post("/logout")
def logout(response: Response, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Add token to blacklist
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expires_at = datetime.fromtimestamp(payload['exp'])
        
        db.add(models.TokenBlacklist(
            token=token,
            expires_at=expires_at
        ))
        db.commit()
        
        
        response.delete_cookie("access_token")
        
        return {"message": "Successfully logged out"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

@router.get("/users/me", response_model=schemas.UserRoleOut)
def read_current_user(user: models.User= Depends(get_current_user)):
    return {"role": user.role}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token, db)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(payload.get("sub"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    print("🪪 Token payload:", payload)
    print("🧑 User ID from token:", user_id)
    print("🔍 User from DB:", user.username, "Role in DB:", user.role)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Make sure role is populated from DB
    print("✅ User from DB:", user.username, "Role:", user.role)

    return user


@router.post("/guest-login")
def guest_login(database: Session = Depends(get_db)):
    guest_user = models.User(
        username=f"guest_{int(datetime.utcnow().timestamp())}",
        email=None,
        hashed_password=None,
        role="guest"
    )
    database.add(guest_user)
    database.commit()
    database.refresh(guest_user)

    # Generate access token for the guest user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(guest_user.id),
        "role": "guest",
        "exp": datetime.utcnow() + access_token_expires
    }
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": guest_user.id
    })

# app/utils/security.py (or wherever you keep it)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
