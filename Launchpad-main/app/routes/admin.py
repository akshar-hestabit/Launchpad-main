from fastapi import APIRouter, Depends
from app.dependencies import admin_only
from app.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/verify-admin")
def verify_admin(current_admin: User = Depends(admin_only)):
    """
    Endpoint to verify that the user is an admin and token is valid.
    """
    return {"detail": "Admin verified", "user": current_admin.username}
