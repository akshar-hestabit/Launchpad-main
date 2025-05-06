# Module: app/routes/users.py


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, dependencies

router = APIRouter()

@router.get("/users", response_model=list[schemas.UserOut])
def get_users(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if current_user.role == "admin":
        return db.query(models.User).all()
    elif current_user.role == "vendor":
        return db.query(models.User).filter(models.User.role == "customer").all()
    else:  # customer
        return [current_user]
