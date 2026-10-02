import uuid
from datetime import date as dt_date
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class GoalBase(SQLModel):
    title: str
    target_amount: Decimal
    deadline: Optional[dt_date] = Field(default=None, nullable=True)
    active: bool = Field(default=True)


class GoalCreate(GoalBase):
    current_amount: Decimal = Decimal("0.00")


class GoalUpdate(SQLModel):
    title: Optional[str] = None
    target_amount: Optional[Decimal] = None
    current_amount: Optional[Decimal] = None
    deadline: Optional[dt_date] = None
    active: Optional[bool] = None


class Goal(GoalBase, table=True):
    __tablename__ = "goals"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    current_amount: Decimal = Decimal("0.00")


class GoalRead(GoalBase):
    id: uuid.UUID
    current_amount: Decimal