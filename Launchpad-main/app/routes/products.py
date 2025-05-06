# Module: app/routes/products.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.dependencies import get_db
from fastapi import Query

ELASTICSEARCH_URL = "http://localhost:9200"
from elasticsearch import Elasticsearch
es = Elasticsearch(ELASTICSEARCH_URL)
INDEX_NAME = "products"


router = APIRouter()

@router.get("/products", response_model=list[schemas.ProductOut])
def all_products(db: Session = Depends(get_db)):
    return db.query(models.Products).all()


@router.get("/products/search")
def search_products(
    keyword: str = Query("", description="Search keyword"),
    min_price: float = Query(0, ge=0, description="Minimum price"),
    max_price: float = Query(99999, ge=0, description="Maximum price"),
    category: str = Query(None, description="Filter by category"),
    brand: str = Query(None, description="Filter by brand")
):
    must_clauses = []
    filter_clauses = []

    if keyword:
        must_clauses.append({
            "multi_match": {
                "query": keyword,
                "fields": ["name", "description"]
            }
        })

    filter_clauses.append({
        "range": {
            "price": {"gte": min_price, "lte": max_price}
        }
    })

    if category:
        filter_clauses.append({"term": {"category.keyword": category}})
    if brand:
        filter_clauses.append({"term": {"brand.keyword": brand}})

    #  wrap in "bool"
    query = {
        "bool": {
            "must": must_clauses,
            "filter": filter_clauses
        }
    }

    res = es.search(index=INDEX_NAME, body={"query": query})

    hits = res["hits"]["hits"]
    return [hit["_source"] for hit in hits]


@router.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
  
    product = db.query(models.Products).filter(models.Products.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail=f"Product Not Found with {product_id}")
    return product

@router.post("/add_product", response_model=schemas.ProductOut)
def add_new_product(product: schemas.ProductCreate, db: Session=Depends(get_db)):
    new_product = models.Products(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    

    product_dict = {
        "id": new_product.id,
        "name": new_product.name,
        "description": new_product.description,
        "price": new_product.price,
        "quantity": new_product.quantity,
        "category": new_product.category_id,
        "brand": new_product.brand,
    }
    
    # Index in Elasticsearch
    es.index(index=INDEX_NAME, id=new_product.id, document=product_dict)
    return new_product

@router.put("/updateProduct/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    updated_product: schemas.ProductCreate,
    db: Session = Depends(get_db)):
    product = db.query(models.Products).get(product_id)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    for field, value in updated_product.model_dump().items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    
   
    product_dict = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "quantity": product.quantity,
        "category": product.category,
        "brand": product.brand,
    }
    
    # Index in Elasticsearch - fixed variable name from existing_product to product
    es.index(index=INDEX_NAME, id=product.id, document=product_dict)

    return product

@router.delete("/deleteProduct/{product_id}")
def delete_by_id(product_id: int, db: Session=Depends(get_db)):
    product = db.query(models.Products).get(product_id)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")      
    
    db.delete(product)      
    db.commit()
    

    try:
        es.delete(index=INDEX_NAME, id=product_id)
    except Exception:
        pass
    
    return {"message": f"Product with id {product_id} deleted successfully"}