from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=schemas.OrderOut, status_code=201)
def create_order(data: schemas.OrderCreate,
                 user: models.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    order = models.Order(user_id=user.id, shipping_address=data.shipping_address)
    total = Decimal("0")
    for item in data.items:
        # lock the row so two people can't buy the last item at the same time
        product = db.scalar(select(models.Product)
                            .where(models.Product.id == item.product_id)
                            .with_for_update())
        if not product or not product.is_active:
            raise HTTPException(404, f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(400, f"Not enough stock for '{product.name}'")
        product.stock -= item.quantity
        total += product.price * item.quantity      # price comes from the DB, not the client
        order.items.append(models.OrderItem(product_id=product.id,
                                            quantity=item.quantity,
                                            unit_price=product.price))
    order.total = total
    db.add(order)
    db.commit()          # everything succeeds together or nothing is saved
    db.refresh(order)
    return order

@router.get("", response_model=list[schemas.OrderOut])
def my_orders(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(models.Order)
                      .where(models.Order.user_id == user.id)
                      .order_by(models.Order.created_at.desc())).all()

@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, user: models.User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    order = db.get(models.Order, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(404, "Order not found")
    return order