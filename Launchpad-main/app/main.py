
from fastapi import FastAPI, Request
from datetime import datetime
from app import auth, models
from app.db import engine, SessionLocal
from app.routes import (
    users, dashboard, products, cart_route,
    stripe_payment, stripe_webhook,
    paypal_payment, paypal_webhook, order_management, invoice,search, crud_wishlist)
from app.utils import(otp, email)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from elasticsearch import Elasticsearch
from sqlalchemy.orm import Session
from app.utils.request_logging import log_requests  
from app.utils.logger import logger
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Optional,List
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5/minute"]
)

# Initialize FastAPI app
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.middleware("http")(log_requests)  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount('/frontend', StaticFiles(directory='frontend'), name='frontend')
app.mount("/static", StaticFiles(directory="frontend"), name="static")
Instrumentator().instrument(app).expose(app, include_in_schema=False)
# Create database tables
models.Base.metadata.create_all(bind=engine)

# Elasticsearch configuration
ELASTICSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "products"
es = Elasticsearch(ELASTICSEARCH_URL)

start_time = datetime.now()

def init_elasticsearch():
    try:
        if not es.ping():
            print(" Could not connect to Elasticsearch")
            return

        if not es.indices.exists(index=INDEX_NAME):
            body = {
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                "mappings": {
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "text"},
                        "description": {"type": "text"},
                        "price": {"type": "float"},
                        "quantity": {"type": "integer"},
                        "category_id": {"type": "integer"},
                        "brand": {"type": "keyword"}
                    }
                }
            }
            es.indices.create(index=INDEX_NAME, body=body)
            print(f" Created Elasticsearch index: {INDEX_NAME}")
        else:
            print(f" Elasticsearch index '{INDEX_NAME}' already exists.")
    except Exception as e:
        print(f" Error initializing Elasticsearch: {str(e)}")

# Reindex products into Elasticsearch
def reindex_products(db: Session):
    products = db.query(models.Products).all()
    for product in products:
        es.index(index=INDEX_NAME, id=product.id, document={
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "category_id": product.category_id,
            "brand": product.brand
        })
    print(f"Reindexed {len(products)} products into Elasticsearch")


@app.on_event("startup")
async def startup_event():
    print("...Starting application...")
    init_elasticsearch()
    db = SessionLocal()
    reindex_products(db)
    db.close()


# ========== Routes =======-
app.include_router(otp.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(products.router)
app.include_router(cart_route.router)
app.include_router(stripe_payment.router)
app.include_router(stripe_webhook.router)
app.include_router(paypal_payment.router)
app.include_router(paypal_webhook.router)
app.include_router(order_management.router)
app.include_router(invoice.router)
app.include_router(search.router)
app.include_router(crud_wishlist.router)
# Health check endpoints
@app.get("/")
def root():
    return {"message": "This is an API for health check"}

@app.get("/check")
def health_check():
    current_time = datetime.now()
    return {
        "status": "OK",
        "uptime": current_time - start_time,
        "current time": current_time,
        "started at": start_time
    }

# frontend static HTML pages
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/login")
async def serve_login_page():
    return FileResponse("frontend/login.html")

@app.get("/signup")
async def serve_signup_page():
    return FileResponse("frontend/signup.html")

@app.get("/products")
async def serve_products_page():
    return FileResponse("frontend/products.html")

@app.get("/cart")
async def serve_cart_page():
    return FileResponse("frontend/cart.html")

@app.get("/wishlist")
async def serve_wishlist_page():
    return FileResponse("frontend/wishlist.html")

@app.get("/checkout")
async def serve_checkout_page():
    return FileResponse("frontend/checkout.html")

@app.get("/orders")
async def serve_orders_page():
    return FileResponse("frontend/orders.html")

@app.get("/payment-success")
def serve_payment_success():
    return FileResponse("frontend/payment-success.html")

@app.get("/signup-page")
def get_signup_page():
    return FileResponse("frontend/signup.html")
