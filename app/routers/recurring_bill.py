import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import RecurringBill, RecurringBillCreate, RecurringBillRead, RecurringBillUpdate

router = APIRouter(prefix="/recurring-bills", tags=["Recurring Bills"])


@router.post("/", response_model=RecurringBillRead, status_code=status.HTTP_201_CREATED)
def create_recurring_bill(bill_in: RecurringBillCreate, session: Session = Depends(get_session)):
    bill = RecurringBill.model_validate(bill_in)
    session.add(bill)
    session.commit()
    session.refresh(bill)
    return bill


@router.get("/", response_model=List[RecurringBillRead])
def list_recurring_bills(
    active_only: bool = True,
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    query = select(RecurringBill)
    if active_only:
        query = query.where(RecurringBill.active == True)
    bills = session.exec(query.offset(offset).limit(limit)).all()
    return bills


@router.get("/{bill_id}", response_model=RecurringBillRead)
def get_recurring_bill(bill_id: uuid.UUID, session: Session = Depends(get_session)):
    bill = session.get(RecurringBill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Conta recorrente não encontrada")
    return bill


@router.patch("/{bill_id}", response_model=RecurringBillRead)
def update_recurring_bill(
    bill_id: uuid.UUID,
    bill_update: RecurringBillUpdate,
    session: Session = Depends(get_session)
):
    bill = session.get(RecurringBill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Conta recorrente não encontrada")
        
    update_data = bill_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bill, key, value)
        
    session.add(bill)
    session.commit()
    session.refresh(bill)
    return bill


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_bill(bill_id: uuid.UUID, session: Session = Depends(get_session)):
    bill = session.get(RecurringBill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Conta recorrente não encontrada")
    session.delete(bill)
    session.commit()
    return None