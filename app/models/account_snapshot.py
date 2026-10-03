import uuid
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint


class AccountSnapshotBase(SQLModel):
    account_id: uuid.UUID = Field(foreign_key="accounts.id", index=True)
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    balance: Decimal = Field(max_digits=12, decimal_places=2)


class AccountSnapshotCreate(AccountSnapshotBase):
    pass


class AccountSnapshotUpdate(SQLModel):
    balance: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)


class AccountSnapshot(AccountSnapshotBase, table=True):
    __tablename__ = "account_snapshots"
    __table_args__ = (
        # Garante que só existe 1 foto por conta em um dado mês/ano
        UniqueConstraint("account_id", "year", "month", name="uq_account_year_month"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class AccountSnapshotRead(AccountSnapshotBase):
    id: uuid.UUID