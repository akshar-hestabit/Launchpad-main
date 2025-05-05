# Module: app/reindex.py
# Brief: TODO - add description

from app.models import Products
from app.elastisearch_client import es  # assuming you have this
from sqlalchemy.orm import Session
from app.auth import get_db

def reindex_products(db: Session):
    products = db.query(Products).all()
    for product in products:
        es.index(index="products", id=product.id, document={
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "category": product.category,
            "brand": product.brand
        })

if __name__ == "__main__":
    db = SessionLocal()
    reindex_products(db)
    db.close()
