# Module: app/routes/paypal_webhook.py


from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
import os
import json

router = APIRouter(prefix="/webhook", tags=["PayPal Webhook"])

@router.post("/paypal")
async def paypal_webhook_listener(request: Request):
    try:
        body_bytes = await request.body()
        if not body_bytes:
            raise HTTPException(status_code=400, detail="Empty request body")

        try:
            event = json.loads(body_bytes)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

        print("🔔 PayPal Webhook Event Received:", event)


        return {"status": "received"}

    except Exception as e:
        print("❌ Webhook Error:", e)
        raise HTTPException(status_code=400, detail="Webhook processing failed")

