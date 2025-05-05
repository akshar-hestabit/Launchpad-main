# Module: app/utils/email.py
# Brief: TODO - add description

import smtplib
from email.message import EmailMessage


def send_email_otp(to_email:str,  otp:str):
    msg = EmailMessage()
    msg['Subject'] = 'OTP Code for verification'
    msg['From'] = 'arastogi23@hotmail.com'
    msg['To'] = to_email

    msg.set_content(f"""
            Your OTP code is: {otp}
            This code expires in 5 minutes.
        """)
    with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
        server.starttls()
        server.login('arastogi23@hotmail.com', 'Smiriti@83')
        server.send_message(msg)

