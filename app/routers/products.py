from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import require_admin

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=list[schemas.ProductOut])
def list_products(search: str | None = None, category_id: int | None = None,
                  skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    query = select(models.Product).where(models.Product.is_active == True)
    if search:
        query = query.where(models.Product.name.ilike(f"%{search}%"))
    if category_id:
        query = query.where(models.Product.category_id == category_id)
    return db.scalars(query.offset(skip).limit(limit)).all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(404, "Product not found")
    return product

@router.post("", response_model=schemas.ProductOut, status_code=201,
             dependencies=[Depends(require_admin)])
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = models.Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/{product_id}", response_model=schemas.ProductOut,
            dependencies=[Depends(require_admin)])
def update_product(product_id: int, data: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    for field, value in data.model_dump().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    product.is_active = False       # soft delete, so old orders keep working
    db.commit()