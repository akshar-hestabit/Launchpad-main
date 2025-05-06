from sqlalchemy.orm import Session
from app.models import Wishlist
from app.schemas import WishlistCreate, WishlistResponse
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from typing import List
from app.db import Base
from app.auth import get_db

router = APIRouter()

def add_to_wishlist(db: Session, wishlist: WishlistCreate):
    # Check if item already exists in wishlist
    existing_item = db.query(Wishlist).filter(
        Wishlist.user_id == wishlist.user_id,
        Wishlist.product_id == wishlist.product_id
    ).first()
    
    if existing_item:
        return None  # Or raise an exception
    
    db_item = Wishlist(**wishlist.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def remove_from_wishlist(db: Session, user_id: int, product_id: int):
    item = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

def get_wishlist_by_user(db: Session, user_id: int):
    return db.query(Wishlist).filter(Wishlist.user_id == user_id).all()



# Add to Wishlist
@router.post("/wishlist/", response_model=WishlistResponse)
def add_item_to_wishlist(
    wishlist: WishlistCreate,
    db: Session = Depends(get_db)
):
    db_item = add_to_wishlist(db, wishlist)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item already in wishlist",
        )
    return db_item

# Remove from Wishlist
@router.delete("/wishlist/{user_id}/{product_id}")
def remove_item_from_wishlist(
    user_id: int,
    product_id: int,
    db: Session = Depends(get_db)
):
    success = remove_from_wishlist(db, user_id, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in wishlist",
        )
    return {"message": "Item removed from wishlist"}

# Get User's Wishlist
@router.get("/wishlist/{user_id}", response_model=List[WishlistResponse])
def get_user_wishlist(user_id: int, db: Session = Depends(get_db)):
    return get_wishlist_by_user(db, user_id)