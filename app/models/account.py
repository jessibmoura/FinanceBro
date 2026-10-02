import uuid
from decimal import Decimal
from typing import Optional
from enum import Enum
from sqlmodel import Field, SQLModel

class AccountType(str, Enum):
    CORRENTE = "CORRENTE"
    POUPANCA = "POUPANCA"
    INVESTIMENTO = "INVESTIMENTO"
    CONTA_SALARIO = "CONTA_SALARIO"

class AccountBase(SQLModel):
    name: str = Field(index=True)
    account_type: AccountType = Field(default=AccountType.CORRENTE)  # ex: CORRENTE, POUPANCA, INVESTIMENTO
    closing_day: Optional[int] = Field(default=None, ge=1, le=31)
    due_day: Optional[int] = Field(default=None, ge=1, le=31)

class AccountCreate(AccountBase):
    balance: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)

class AccountUpdate(SQLModel):
    name: Optional[str] = None
    account_type: Optional[AccountType] = None
    balance: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    closing_day: Optional[int] = Field(default=None, ge=1, le=31)
    due_day: Optional[int] = Field(default=None, ge=1, le=31)


class Account(AccountBase, table=True):
    __tablename__ = "accounts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    balance: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)


class AccountRead(AccountBase):
    pass