from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.config import Config
from app.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth import get_db
from app import models
from datetime import timedelta
import os
from sqlalchemy.orm import Session
# Initialize router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth configuration
config = Config(".env")
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
    authorize_params={"access_type": "offline", "prompt": "consent"}
)


@router.get("/google")
async def login_via_google(request: Request):
    redirect_url = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_url)

@router.get("/google/callback")
async def auth_google_callback(
    request: Request, 
    db: Session = Depends(get_db)
):
    try:

        token = await oauth.google.authorize_access_token(request)
        
        if not token.get('id_token'):
            raise HTTPException(status_code=400, detail="Missing id_token in Google response")      
        
        #print(token)
        user_info = await oauth.google.parse_id_token(request, token)
        print(f"this is user info********************************************************************_______*********{user_info}")
        email = user_info.get("email")
        name = user_info.get("name")
        
        if not email:
            return RedirectResponse(url="/auth/failed?error=no_email")
            
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            user = models.User(
                username=email.split("@")[0],
                email=email,
                full_name=name,
                hashed_password="",  # Empty for OAuth users
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Redirect to frontend with token
        frontend_url = f"{os.getenv('FRONTEND_URL')}/frontend/dashboard?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        #return RedirectResponse(url=f"/auth/failed?error={str(e)}")
        print(f"error is :::::: {e}")
        return e