import uuid
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    name: str = Field(index=True)
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id", nullable=True)
    monthly_budget: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2, nullable=True)
    icon: Optional[str] = Field(
        default=None, 
        description="Nome/caminho do arquivo na pasta imgs (ex: grocery.png) ou emoji (ex: 🛒)"
    )


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    monthly_budget: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    icon: Optional[str] = None


class Category(CategoryBase, table=True):
    __tablename__ = "categories"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class CategoryRead(CategoryBase):
    id: uuid.UUID