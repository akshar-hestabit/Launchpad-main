from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app import models, schemas
from app.models import Products, Order, OrderItem
from app.schemas import OrderOut, OrderCreate
from datetime import datetime
from app.auth import get_db, get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

def create_order(order_data: OrderCreate, db: Session):
    total_price = 0
    product_update = []
    for item in order_data.items:
        product = db.query(Products).filter(Products.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {item.product_id}")
        total_price += product.price * item.quantity
        product.quantity -= item.quantity
        product_update.append(product)
    new_order = Order(
        user_id=order_data.user_id,
        total_price=total_price,
        status=order_data.status or "PENDING",
        payment_method=order_data.payment_method,
        created_at=datetime.utcnow()
    )
    db.add(new_order)
    db.flush()
    for item in order_data.items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=db.query(Products).get(item.product_id).price
        )
        db.add(order_item)
    for product in product_update:
        db.add(product)
    db.commit()
    db.refresh(new_order)
    new_order_with_items = db.query(Order).options(joinedload(Order.items)).filter(Order.id == new_order.id).first()
    return new_order_with_items

def get_orders_by_id(user_id: int, db: Session):
    return db.query(Order).filter(Order.user_id == user_id).all()

def get_orders_by_order_id(order_id: int, db: Session):
    orders = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not orders:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
    return orders

def get_all_orders(db: Session):
    return db.query(Order).all()

def update_order_status(order_id: int, status: str, db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
    order.status = status
    db.commit()
    db.refresh(order)
    return order

@router.post("/create_order", response_model=OrderOut)
def create_new_order(order: OrderCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if user.id != order.user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create order for another user")
    return create_order(order, db)

@router.get("/orders/{user_id}", response_model=list[OrderOut])
def get_orders_for_user(user_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if user.id != user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return get_orders_by_id(user_id, db)

@router.get("/all_orders", response_model=list[OrderOut])
def get_all_orders_route(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return get_all_orders(db)

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = get_orders_by_order_id(order_id, db)
    if order.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your order")
    return order
