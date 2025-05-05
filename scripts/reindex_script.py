# Module: reindex_script.py
# Brief: TODO - add description

from models import Products
from elastisearch_client import es  # assuming you have this
from sqlalchemy.orm import Session
from auth import get_db

def reindex_products(db: Session):
    products = db.query(Products).all()
    for product in products:
        es.index(index="products", id=product.id, document={
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "category": product.category,
            "brand": product.brand,
            "vendor": product.vendor
        })
