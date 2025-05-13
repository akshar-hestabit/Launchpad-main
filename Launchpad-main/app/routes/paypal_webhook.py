from fastapi import APIRouter, Request, HTTPException, Depends
import requests
import os
import json
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.auth import get_db
from app.schemas import OrderCreate, OrderItemCreate
from app.routes.order_management import create_order  

load_dotenv()

router = APIRouter(prefix="/webhook", tags=["PayPal Webhook"])

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID")

def get_paypal_access_token():
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET))
    if response.status_code != 200:
        print("Failed to get PayPal access token:", response.text)
        raise HTTPException(status_code=500, detail="Failed to get PayPal access token")
    return response.json()["access_token"]

def verify_paypal_webhook_signature(headers, body):
    access_token = get_paypal_access_token()
    url = f"{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature"
    verify_data = {
        "auth_algo": headers.get("paypal-auth-algo"),
        "cert_url": headers.get("paypal-cert-url"),
        "transmission_id": headers.get("paypal-transmission-id"),
        "transmission_sig": headers.get("paypal-transmission-sig"),
        "transmission_time": headers.get("paypal-transmission-time"),
        "webhook_id": PAYPAL_WEBHOOK_ID,
        "webhook_event": body,
    }
    verify_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.post(url, headers=verify_headers, json=verify_data)
    if response.status_code != 200:
        print("PayPal webhook verification failed:", response.text)
        return False
    result = response.json()
    print("PayPal verification result:", result)
    return result.get("verification_status") == "SUCCESS"

@router.post("/paypal")
async def paypal_webhook_listener(request: Request, db: Session = Depends(get_db)):
    body_bytes = await request.body()
    try:
        body_json = json.loads(body_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    headers = {k.lower(): v for k, v in request.headers.items()}
    is_valid = verify_paypal_webhook_signature(headers, body_json)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Webhook signature verification failed")

    event_type = body_json.get('event_type')
    resource = body_json.get('resource', {})

    print(f"PayPal Webhook Received - Event: {event_type}")

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
    
        purchase_unit = resource.get("purchase_units", [{}])[0]
        user_id = int(purchase_unit.get("custom_id"))
        items = purchase_unit.get("items", [])
        total_price = float(purchase_unit["amount"]["value"])
        payment_method = "PAYPAL"
        status = "COMPLETED"


        order_items = [OrderItemCreate(product_id=int(item["product_id"]), quantity=int(item["quantity"])) for item in items]

        order_data = OrderCreate(
            user_id=user_id,
            total_price=total_price,
            payment_method=payment_method,
            status=status,
            items=order_items
        )

        try:
            create_order(order_data, db)
            print("Order created for user:", user_id)
        except Exception as e:
            print("Order creation failed:", e)

    return {"status": "success", "event_type": event_type}
