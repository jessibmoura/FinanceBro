import uuid
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class RecurringBillBase(SQLModel):
    title: str
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    due_day: int = Field(ge=1, le=31)
    category_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id", nullable=True)
    account_id: Optional[uuid.UUID] = Field(default=None, foreign_key="accounts.id", nullable=True)
    active: bool = Field(default=True)


class RecurringBillCreate(RecurringBillBase):
    pass


class RecurringBillUpdate(SQLModel):
    title: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    due_day: Optional[int] = Field(default=None, ge=1, le=31)
    category_id: Optional[uuid.UUID] = None
    account_id: Optional[uuid.UUID] = None
    active: Optional[bool] = None


class RecurringBill(RecurringBillBase, table=True):
    __tablename__ = "recurring_bills"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class RecurringBillRead(RecurringBillBase):
    pass