# Module: app/routes/stripe_payment.py


import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeCheckoutRequest(BaseModel):
    amount : float
    currency:str = 'usd'
    product_name: str

@router.post("/create-checkout-session")
async def create_checkout_session(data: StripeCheckoutRequest):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": data.currency,
                        "product_data": {
                            "name": data.product_name,
                        },
                        "unit_amount": int(data.amount * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://127.0.0.1:8000/frontend/success.html",
            cancel_url="http://127.0.0.1:8000/frontend/cancel.html",
        )
        return JSONResponse({"checkout_url": session.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
