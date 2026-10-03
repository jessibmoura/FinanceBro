import uuid
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Account, AccountSnapshot, AccountSnapshotCreate, AccountSnapshotRead, AccountSnapshotUpdate

router = APIRouter(prefix="/snapshots", tags=["Snapshots"])


@router.post("/", response_model=AccountSnapshotRead, status_code=status.HTTP_201_CREATED)
def create_snapshot(snapshot_in: AccountSnapshotCreate, session: Session = Depends(get_session)):
    # Verifica se já existe snapshot para essa conta no mesmo mês/ano
    existing = session.exec(
        select(AccountSnapshot).where(
            AccountSnapshot.account_id == snapshot_in.account_id,
            AccountSnapshot.year == snapshot_in.year,
            AccountSnapshot.month == snapshot_in.month
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Já existe um snapshot registrado para esta conta neste mês/ano. Use o PATCH para atualizar."
        )
        
    snapshot = AccountSnapshot.model_validate(snapshot_in)
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot


@router.post("/capture-current-month", response_model=List[AccountSnapshotRead])
def capture_current_month_snapshot(session: Session = Depends(get_session)):
    """
    Captura o saldo atual de TODAS as contas e salva como snapshot do mês vigente.
    Se já existir snapshot no mês para a conta, atualiza com o saldo atual.
    """
    today = date.today()
    accounts = session.exec(select(Account)).all()
    saved_snapshots = []

    for acc in accounts:
        snapshot = session.exec(
            select(AccountSnapshot).where(
                AccountSnapshot.account_id == acc.id,
                AccountSnapshot.year == today.year,
                AccountSnapshot.month == today.month
            )
        ).first()

        if snapshot:
            snapshot.balance = acc.balance
        else:
            snapshot = AccountSnapshot(
                account_id=acc.id,
                year=today.year,
                month=today.month,
                balance=acc.balance
            )
            session.add(snapshot)

        session.commit()
        session.refresh(snapshot)
        saved_snapshots.append(snapshot)

    return saved_snapshots


@router.get("/", response_model=List[AccountSnapshotRead])
def list_snapshots(
    year: Optional[int] = None,
    month: Optional[int] = None,
    account_id: Optional[uuid.UUID] = None,
    session: Session = Depends(get_session)
):
    query = select(AccountSnapshot)
    if year:
        query = query.where(AccountSnapshot.year == year)
    if month:
        query = query.where(AccountSnapshot.month == month)
    if account_id:
        query = query.where(AccountSnapshot.account_id == account_id)
        
    return session.exec(query.order_by(AccountSnapshot.year.desc(), AccountSnapshot.month.desc())).all()


@router.delete("/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snapshot(snapshot_id: uuid.UUID, session: Session = Depends(get_session)):
    snapshot = session.get(AccountSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot não encontrado")
    session.delete(snapshot)
    session.commit()
    return None