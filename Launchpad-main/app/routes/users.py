

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, dependencies

router = APIRouter()

@router.get("/users", response_model=list[schemas.UserOut])
async def get_users(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    # Only admin can access all users
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view users")
    
    return db.query(models.User).all()