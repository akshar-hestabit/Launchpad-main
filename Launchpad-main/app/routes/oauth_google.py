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
        # Get the token from Google OAuth
        print("Starting Google OAuth callback...")
        token = await oauth.google.authorize_access_token(request)
        print(f"Received token: {token}")
        
        # Make sure we have an access token
        if 'access_token' not in token:
            print("No access token in response")
            return RedirectResponse(url="/login?error=no_access_token")
        
        # Get user info directly using the access token
        try:
            # Use the token directly
            resp = await oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo', token=token)
            user_info = resp.json()
            print(f"User info from Google: {user_info}")
        except Exception as userinfo_error:
            print(f"Error getting user info: {userinfo_error}")
            return RedirectResponse(url="/login?error=user_info_failed")
        
        email = user_info.get("email")
        name = user_info.get("name", "Google User")
        
        if not email:
            print("No email in user info")
            return RedirectResponse(url="/login?error=no_email")
            
        print(f"Login attempt for Google user: {email}")
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            print(f"Creating new user for Google account: {email}")
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
        frontend_url = f"http://localhost:8000/frontend/dashboard.html?token={access_token}"
        print(f"Redirecting to: {frontend_url}")
        
        # Make sure we return a proper redirect with status code 302
        response = RedirectResponse(url=frontend_url)
        response.status_code = 302
        return response
        
    except Exception as e:
        print(f"Error in Google OAuth callback: {e}")
        import traceback
        traceback.print_exc()
        # Return a more user-friendly error page with a 302 redirect
        response = RedirectResponse(url="/login?error=auth_failed")
        response.status_code = 302
        return response