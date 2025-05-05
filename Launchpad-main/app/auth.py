# Module: app/auth.py
# Brief: TODO - add description

#this file is for signup logic 

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models, db
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
router  = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()

def get_db():
    database = db.SessionLocal()
    try:
        yield database
    finally:
        database.close()

@router.post("/signup", response_model= schemas.UserOut)
def signup(user: schemas.UserCreate, database: Session = Depends(get_db)):
    existing = database.query(models.User).filter(models.User.username== user.username).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_pw = pwd_context.hash(user.password)
    new_user = models.User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_pw,
        role = user.role
    )

    database.add(new_user)
    database.commit()
    database.refresh(new_user)
    return new_user


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError()
        return username
    except JWTError:
        return None


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Debug prints
    # print(f"SECRET_KEY type: {type(SECRET_KEY)}")
    # print(f"SECRET_KEY exists: {SECRET_KEY is not None}")
    # print(f"SECRET_KEY length: {len(SECRET_KEY) if SECRET_KEY else 'N/A'}")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
