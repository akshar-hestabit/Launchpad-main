import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os
from dotenv import load_dotenv

load_dotenv() 

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger 
logger = logging.getLogger("launchpad")
logger.setLevel(logging.DEBUG)


file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=1_000_000,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

#Existing Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

#  Email Alert Handler
email_handler = SMTPHandler(
    mailhost=("smtp.gmail.com", 587),  
    fromaddr=os.getenv("ALERT_EMAIL"),
    toaddrs=[os.getenv("ADMIN_EMAIL")],
    subject="LAUNCHPAD CRITICAL ERROR",
    credentials=(os.getenv("ALERT_EMAIL"), os.getenv("ALERT_EMAIL_PASSWORD")),
    secure=()  # Enables STARTTLS
)
email_handler.setLevel(logging.CRITICAL)  
email_handler.setFormatter(logging.Formatter('''
Time: %(asctime)s
Level: %(levelname)s
Message: %(message)s
'''))

# Add all handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.addHandler(email_handler)