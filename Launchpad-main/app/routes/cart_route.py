# Module: app/routes/cart_route.py


from fastapi import APIRouter,FastAPI, HTTPException
from app.routes.redis_file.carts import add_to_cart, remove_from_cart, clear_cart, view_cart

router = APIRouter()


@router.get("/cart/{user_id}")
def get_cart(user_id: int):
    cart = view_cart(user_id)
    return {"cart":cart}

@router.post("/cart/add")
def add_cart(user_id:int, product_id: int, quantity: int=1):
    return add_to_cart(user_id, product_id, quantity)

@router.post("/cart/remove")
def remove_cart(user_id: int, product_id: int):
    return remove_from_cart(user_id, product_id)

@router.delete("/cart/delete")
def delete_cart(user_id: int):
    return clear_cart(user_id)