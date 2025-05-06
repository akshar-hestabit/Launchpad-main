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
async def create_checkout_session(data:StripeCheckoutRequest):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data":{
                        "currency": data.currency,
                        "product_data":{
                            "name": data.product_name,
                        },
                            "unit_amount": int(data.amount*100)},#we multiply by 100 for all zero decimeled currencies
                            "quantity":1,
                }
            ],
            mode="payment",
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel",
        )
        return JSONResponse({"checkout_url": session.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

