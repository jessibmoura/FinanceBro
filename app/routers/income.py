import uuid
from typing import List, Optional
from datetime import date as dt_date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Income, IncomeCreate, IncomeRead, IncomeUpdate

router = APIRouter(prefix="/incomes", tags=["Incomes"])


@router.post("/", response_model=IncomeRead, status_code=status.HTTP_201_CREATED)
def create_income(income_in: IncomeCreate, session: Session = Depends(get_session)):
    income = Income.model_validate(income_in)
    session.add(income)
    session.commit()
    session.refresh(income)
    return income


@router.get("/", response_model=List[IncomeRead])
def list_incomes(
    start_date: Optional[dt_date] = None,
    end_date: Optional[dt_date] = None,
    account_id: Optional[uuid.UUID] = None,
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    query = select(Income)
    if start_date:
        query = query.where(Income.income_date >= start_date)
    if end_date:
        query = query.where(Income.income_date <= end_date)
    if account_id:
        query = query.where(Income.account_id == account_id)
        
    incomes = session.exec(query.order_by(Income.income_date.desc()).offset(offset).limit(limit)).all()
    return incomes


@router.get("/{income_id}", response_model=IncomeRead)
def get_income(income_id: uuid.UUID, session: Session = Depends(get_session)):
    income = session.get(Income, income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    return income


@router.patch("/{income_id}", response_model=IncomeRead)
def update_income(
    income_id: uuid.UUID,
    income_update: IncomeUpdate,
    session: Session = Depends(get_session)
):
    income = session.get(Income, income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
        
    update_data = income_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(income, key, value)
        
    session.add(income)
    session.commit()
    session.refresh(income)
    return income


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: uuid.UUID, session: Session = Depends(get_session)):
    income = session.get(Income, income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    session.delete(income)
    session.commit()
    return None