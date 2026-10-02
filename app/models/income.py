import uuid
from datetime import date as dt_date
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel

class IncomeBase(SQLModel):
    title: str
    amount: Decimal
    income_date: dt_date = Field(default_factory=dt_date.today, index=True)
    is_recurring: bool = Field(default=False)
    account_id: Optional[uuid.UUID] = Field(default=None, foreign_key="accounts.id", nullable=True)

class IncomeCreate(IncomeBase):
    pass

class IncomeUpdate(SQLModel):
    title: Optional[str] = None
    amount: Optional[Decimal] = None
    income_date: Optional[dt_date] = None
    is_recurring: Optional[bool] = None
    account_id: Optional[uuid.UUID] = None


class Income(IncomeBase, table=True):
    __tablename__ = "incomes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class IncomeRead(IncomeBase):
    id: uuid.UUID