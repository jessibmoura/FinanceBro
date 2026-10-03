import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Account, AccountCreate, AccountRead, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(account_in: AccountCreate, session: Session = Depends(get_session)):
    account = Account.model_validate(account_in)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.get("/", response_model=List[AccountRead])
def list_accounts(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    accounts = session.exec(select(Account).offset(offset).limit(limit)).all()
    return accounts


@router.get("/{account_id}", response_model=AccountRead)
def get_account(account_id: uuid.UUID, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return account


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(
    account_id: uuid.UUID,
    account_update: AccountUpdate,
    session: Session = Depends(get_session)
):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    update_data = account_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
        
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: uuid.UUID, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    session.delete(account)
    session.commit()
    return None