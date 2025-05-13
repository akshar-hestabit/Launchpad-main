import requests
import os
from fastapi import APIRouter, HTTPException, Body
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/paypal", tags=["PayPal"])

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"  

def get_paypal_access_token():
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET))
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get PayPal access token")
    return response.json()["access_token"]

@router.post("/create-order")
def create_paypal_order(
    amount: float = Body(...),
    user_id: int = Body(...),
    items: list = Body(...)
):
    access_token = get_paypal_access_token()
    url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": amount
            },
            "custom_id": str(user_id),  
            "items": items              
        }],
        "application_context": {
            "return_url": "http://localhost:3000/payment-success",
            "cancel_url": "http://localhost:3000/payment-cancel"
        }
    }
    response = requests.post(url, headers=headers, json=order_data)
    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="Failed to create PayPal order")
    return response.json()

@router.post("/capture-order/{order_id}")
def capture_paypal_order(order_id: str):
    access_token = get_paypal_access_token()
    url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(url, headers=headers)
    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="Failed to capture PayPal order")
    return response.json()
