#this file prevents circular imports 
# app/utils.py

from jose import JWTError, jwt
from fastapi import HTTPException, status
from app import schemas

SECRET_KEY = "secret_key_here"
ALGORITHM = "HS256"

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return schemas.TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception

