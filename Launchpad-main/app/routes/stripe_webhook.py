from fastapi import APIRouter, Request, HTTPException, Depends
import stripe
import os
import json
from app.auth import get_db
from sqlalchemy.orm import Session
from app.schemas import OrderCreate, OrderItemCreate
from app.routes.order_management import create_order
from dotenv import load_dotenv
from prometheus_client import Counter

load_dotenv()

router = APIRouter(prefix="/stripe")
STRIPE_WEBHOOK_KEY = os.getenv("STRIPE_WEBHOOK_KEY")

stripe_failed_webhooks_total = Counter(
    "stripe_failed_webhooks_total", "Total failed Stripe transactions"
)

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_KEY)
    except ValueError:
        stripe_failed_webhooks_total.inc()
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        stripe_failed_webhooks_total.inc()
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})

        try:
            user_id = int(metadata.get("user_id"))
            cart = json.loads(metadata.get("cart", "[]"))
        except Exception:
            stripe_failed_webhooks_total.inc()
            return {"status": "skipped"}

        try:
            total_price = sum(item["price"] * item["quantity"] for item in cart)
            payment_method = "STRIPE"
            status = "COMPLETED"
            order_items = [
                OrderItemCreate(product_id=item["product_id"], quantity=item["quantity"])
                for item in cart
            ]
            order_data = OrderCreate(
                user_id=user_id,
                total_price=total_price,
                payment_method=payment_method,
                status=status,
                items=order_items
            )
            create_order(order_data, db)
        except Exception:
            stripe_failed_webhooks_total.inc()

    return {"status": "success"}