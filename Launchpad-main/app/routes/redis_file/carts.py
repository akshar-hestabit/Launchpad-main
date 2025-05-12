# Module: app/routes/redis_file/carts.py
# Brief: TODO - add description

import redis
from fastapi import FastAPI, HTTPException


r = redis.Redis(host='localhost', port=6379,db=0, decode_responses=True)
app = FastAPI()

CART_EXPIRATION_SECONDS = 60 * 30 

def add_to_cart(user_id: int, product_id: int, quantity: int):
    cart_key = f"cart:{user_id}"


    cart = r.hgetall(cart_key)


    if str(product_id) in cart:
        current_quantity = int(cart[str(product_id)])
        r.hset(cart_key, product_id, current_quantity + quantity)
    else:
        r.hset(cart_key, product_id, quantity)

    r.expire(cart_key, CART_EXPIRATION_SECONDS)

    return {"message": "Product added to cart."}


def remove_from_cart(user_id:int, product_id: int):
    r.hdel(f"cart:{user_id}", product_id)
    return {"message": "Product removed from cart"}

def view_cart(user_id: int):
    cart = r.hgetall(f"cart:{user_id}")
    if not cart:
        return {"message" :"Empty Cart"}
    return cart

def clear_cart(user_id: int):
    r.delete(f"cart:{user_id}")
    return {"message" : "cart cleared successfully "}
