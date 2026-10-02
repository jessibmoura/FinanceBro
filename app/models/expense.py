import uuid
from datetime import date as dt_date
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class PaymentMethod(str, Enum):
    PIX = "PIX"
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    CASH = "CASH"
    TRANSFER = "TRANSFER"

class ExpenseBase(SQLModel):
    description: str
    amount: Decimal
    expense_date: dt_date = Field(default_factory=dt_date.today, index=True)
    payment_method: PaymentMethod = Field(default=PaymentMethod.PIX)
    account_id: Optional[uuid.UUID] = Field(default=None, foreign_key="accounts.id", nullable=True)
    category_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id", nullable=True)
    installment_number: Optional[int] = Field(default=None, nullable=True)
    total_installments: Optional[int] = Field(default=None, nullable=True)
    installment_group_id: Optional[uuid.UUID] = Field(default=None, nullable=True)
    recurring_bill_id: Optional[uuid.UUID] = Field(default=None, foreign_key="recurring_bills.id", nullable=True)


class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(SQLModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    expense_date: Optional[dt_date] = None
    payment_method: Optional[PaymentMethod] = None
    account_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None

class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class ExpenseRead(ExpenseBase):
    id: uuid.UUID