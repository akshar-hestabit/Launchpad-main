# Module: app/routes/stripe_webhook.py
# Brief: TODO - add description

# routes/stripe_webhook.py
from fastapi import APIRouter, Request, HTTPException
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
endpoint_secret = os.getenv("STRIPE_WEBHOOK_KEY")

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle successful payment
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("✅ Payment received for:", session["id"])

    return {"status": "success"}
