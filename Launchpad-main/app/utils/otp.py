# Module: app/utils/otp.py
# Brief: TODO - add description

# import random
# from fastapi import APIRouter, HTTPException
# from app.utils.email import send_email_otp
# def generate_otp() ->str:
#     return str(random.randint(100000,999999))

# router = APIRouter()

# @router.post("/send_otp")
# async def send_otp(email: str):
#     try:
#         otp = generate_otp()
#         send_email_otp(email, otp)
#         print(f"OTP: {otp} sent to {email}")
#         return {"Message":"OTP Sent successfully", "OTP":otp}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Failed to send OTP")

import random
import string
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional

# In-memory storage for OTPs (replace with database in production)
otp_store: Dict[str, Dict] = {}

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USERNAME = "aksharrastogirocks@gmail.com"
EMAIL_PASSWORD = "kxuw bljp rowt ovzp "  
OTP_EXPIRY_SECONDS = 300  # 5 minutes

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

router = APIRouter()

def generate_otp(length=6) -> str:
    """Generate a numeric OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def store_otp(email: str, otp: str) -> dict:
    """Store OTP with expiration time"""
    expiry_time = int(time.time()) + OTP_EXPIRY_SECONDS
    otp_data = {
        "otp": otp,
        "created_at": int(time.time()),
        "expires_at": expiry_time,
        "is_used": False
    }
    otp_store[email] = otp_data
    return otp_data

def verify_otp(email: str, otp_to_verify: str) -> bool:
    """Verify if OTP is valid and not expired"""
    if email not in otp_store:
        return False
    
    otp_data = otp_store[email]
    current_time = int(time.time())
    
    # Check if OTP is correct, not expired, and not used
    if (otp_data["otp"] == otp_to_verify and 
        otp_data["expires_at"] > current_time and 
        not otp_data["is_used"]):
        
        otp_data["is_used"] = True
        return True
    
    return False

def send_email_otp(to_email: str, otp: str):
    """Send OTP via email with improved HTML formatting"""
    # Calculate expiry time for user-friendly message
    expiry_time = datetime.now() + timedelta(seconds=OTP_EXPIRY_SECONDS)
    expiry_time_str = expiry_time.strftime("%H:%M:%S")
    
    # Create message
    msg = MIMEMultipart()
    msg['Subject'] = 'OTP Code for Verification'
    msg['From'] = EMAIL_USERNAME
    msg['To'] = to_email
    
    # Plain text version
    text_body = f"""
Your verification code is: {otp}

This code will expire at {expiry_time_str}.
Do not share this code with anyone.

If you didn't request this code, please ignore this message.
"""
    
    # HTML version
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
        <h2 style="color: #333;">Your Verification Code</h2>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; font-size: 24px; letter-spacing: 5px; font-weight: bold; margin: 20px 0;">
            {otp}
        </div>
        <p>This code will expire at <strong>{expiry_time_str}</strong>.</p>
        <p style="color: #777; font-size: 14px;">If you didn't request this code, please ignore this message.</p>
        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">This is an automated message. Please do not reply to this email.</p>
    </div>
</body>
</html>
"""
    
    # Attach both versions
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    # Send email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)

def send_success_notification(to_email: str):
    """Send successful verification notification"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    msg = MIMEMultipart()
    msg['Subject'] = 'Authentication Successful'
    msg['From'] = EMAIL_USERNAME
    msg['To'] = to_email
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
        <h2 style="color: #333;">Authentication Successful</h2>
        <p>Your account was successfully authenticated using two-factor authentication.</p>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Time:</strong> {current_time}</p>
        </div>
        <p style="color: #777; font-size: 14px;">If this wasn't you, please contact our support team immediately.</p>
    </div>
</body>
</html>
"""
    
    msg.attach(MIMEText(html_body, 'html'))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)

# FASTAPI ROUTES

@router.post("/send_otp")
async def send_otp_route(request: OTPRequest, background_tasks: BackgroundTasks):
    """Route to generate and send OTP"""
    try:
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP
        store_otp(request.email, otp)
        
        # Send OTP email in background to improve response time
        background_tasks.add_task(send_email_otp, request.email, otp)
        
        
        return {"message": "OTP sent successfully", "otp": otp}
        
 
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

@router.post("/verify_otp")
async def verify_otp_route(request: OTPVerifyRequest, background_tasks: BackgroundTasks):
    """Route to verify OTP"""
    is_valid = verify_otp(request.email, request.otp)
    
    if is_valid:
        
        background_tasks.add_task(send_success_notification, request.email)
        return {"message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
