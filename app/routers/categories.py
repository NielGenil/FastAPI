from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import require_admin

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[schemas.CategoriesOut])
def list_categories(search: str | None = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    query = select(models.Category)
    if search:
        query = query.where(models.Category.name.ilike(f"%{search}%"))
    return db.scalars(query.offset(skip).limit(limit)).all()

@router.get("/{category_id}", response_model=schemas.CategoriesOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    return category

@router.post("", status_code=201, response_model=schemas.CategoriesOut, dependencies=[Depends(require_admin)])
def create_categories(data:schemas.CategoriesCreate, db: Session = Depends(get_db)):
    categories = models.Category(**data.model_dump())
    db.add(categories)
    db.commit()
    db.refresh(categories)
    return categories

@router.put("/{category_id}", response_model=schemas.CategoriesOut, dependencies=[Depends(require_admin)])
def update_categories(category_id: int, data: schemas.CategoriesCreate, db: Session = Depends(get_db)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    for field, value in data.model_dump().items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category

@router.patch("/{category_id}", response_model=schemas.CategoriesOut, dependencies=[Depends(require_admin)])
def patch_categories(category_id: int, data: schemas.CategoriesUpdate, db: Session = Depends(get_db)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    for field, value in data.model_dump().items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    db.delete(category)
    db.commit()


