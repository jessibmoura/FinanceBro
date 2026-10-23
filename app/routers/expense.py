import uuid
from typing import List, Optional
from datetime import date as dt_date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Expense, ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/add_expenses", response_model=List[ExpenseRead], status_code=status.HTTP_201_CREATED)
def create_expenses(expenses_in: List[ExpenseCreate], session: Session = Depends(get_session)):
    if not expenses_in:
        return []
    # Converte os schemas de entrada para instâncias do modelo de banco
    db_expenses = [Expense.model_validate(exp) for exp in expenses_in]
    session.add_all(db_expenses)
    session.commit()
    for exp in db_expenses:
        session.refresh(exp)
    return db_expenses


@router.get("/", response_model=List[ExpenseRead])
def list_expenses(
    start_date: Optional[dt_date] = None,
    end_date: Optional[dt_date] = None,
    account_id: Optional[uuid.UUID] = None,
    category_id: Optional[uuid.UUID] = None,
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    query = select(Expense)
    if start_date:
        query = query.where(Expense.expense_date >= start_date)
    if end_date:
        query = query.where(Expense.expense_date <= end_date)
    if account_id:
        query = query.where(Expense.account_id == account_id)
    if category_id:
        query = query.where(Expense.category_id == category_id)
        
    expenses = session.exec(query.order_by(Expense.expense_date.desc()).offset(offset).limit(limit)).all()
    return expenses


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: uuid.UUID, session: Session = Depends(get_session)):
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: uuid.UUID,
    expense_update: ExpenseUpdate,
    session: Session = Depends(get_session)
):
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
        
    update_data = expense_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)
        
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: uuid.UUID, session: Session = Depends(get_session)):
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    session.delete(expense)
    session.commit()
    return None

@router.delete("/clear-all/", status_code=status.HTTP_200_OK)
def clear_all_expenses(session: Session = Depends(get_session)):
    total_deletado = session.query(Expense).delete()
    session.commit()
    return {"message": f"{total_deletado} despesas removidas com sucesso."}