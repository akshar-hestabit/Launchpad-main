# app/routes/stripe_payment.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import stripe
import json

router = APIRouter(prefix="/stripe")

class StripeCheckoutRequest(BaseModel):
    amount: float
    product_name: str
    user_id: int
    cart: List[Dict]  # Must match frontend structure
    currency: str = "usd"  # Optional default

import stripe
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Must be set before any Stripe calls

@router.post("/create-checkout-session")
async def create_checkout_session(data: StripeCheckoutRequest):
    try:
        # Debug: Print incoming data
        print("Received data:", data.model_dump())
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": data.currency,
                    "product_data": {"name": data.product_name},
                    "unit_amount": int(data.amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://127.0.0.1:8000/frontend/payment-success.html",
            cancel_url="http://127.0.0.1:8000/frontend/payment_cancel.html",
            metadata={
                "user_id": str(data.user_id),
                "cart": json.dumps(data.cart)
            }
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))