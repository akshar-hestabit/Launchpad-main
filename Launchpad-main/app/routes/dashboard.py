# Module: app/routes/dashboard.py


from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app import models

router = APIRouter()

@router.get("/dashboard")
def get_dashboard(user: models.User = Depends(get_current_user)):
    if user.role == "admin":
        return {"message": "Welcome Admin!"}
    elif user.role == "vendor":
        return {"message": "Vendor Dashboard"}
    else:
        return {"message": "Customer Area"}
