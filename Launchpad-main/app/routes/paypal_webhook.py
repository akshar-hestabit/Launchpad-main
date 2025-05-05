# Module: app/routes/paypal_webhook.py
# Brief: TODO - add description

from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
import os
import json

router = APIRouter(prefix="/webhook", tags=["PayPal Webhook"])

@router.post("/paypal")
async def paypal_webhook_listener(request: Request):
    try:
        body = await request.body()
        event = json.loads(body)

        # Log for debugging — remove in production
        print("🔔 PayPal Webhook Event Received:", event)

        event_type = event.get("event_type")
        resource = event.get("resource", {})

        # Example: handle successful payment capture
        if event_type == "CHECKOUT.ORDER.APPROVED":
            order_id = resource.get("id")
            payer = resource.get("payer", {})
            print(f"✅ Order Approved: {order_id}")
            # Update order status in DB here

        elif event_type == "PAYMENT.CAPTURE.COMPLETED":
            capture_id = resource.get("id")
            amount = resource.get("amount", {}).get("value")
            currency = resource.get("amount", {}).get("currency_code")
            print(f"💰 Payment Captured: {capture_id} — {amount} {currency}")
            # Update order/payment table here

        else:
            print(f"⚠️ Unhandled Event Type: {event_type}")

        return {"status": "received"}

    except Exception as e:
        print("❌ Webhook Error:", e)
        raise HTTPException(status_code=400, detail="Webhook processing failed")
