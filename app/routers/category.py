import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Category, CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, session: Session = Depends(get_session)):
    if category_in.parent_id:
        parent = session.get(Category, category_in.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Categoria pai não existe")
            
    category = Category.model_validate(category_in)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/", response_model=List[CategoryRead])
def list_categories(
    parent_only: bool = False,
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    query = select(Category)
    if parent_only:
        query = query.where(Category.parent_id == None)
    categories = session.exec(query.offset(offset).limit(limit)).all()
    return categories


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: uuid.UUID, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: uuid.UUID,
    category_update: CategoryUpdate,
    session: Session = Depends(get_session)
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
    update_data = category_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
        
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: uuid.UUID, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    session.delete(category)
    session.commit()
    return None