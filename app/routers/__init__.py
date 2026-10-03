from app.routers.account import router as accounts_router
from app.routers.category import router as categories_router
from app.routers.recurring_bill import router as recurring_bills_router
from app.routers.expense import router as expenses_router
from app.routers.income import router as incomes_router
from app.routers.goal import router as goals_router

__all__ = [
    "accounts_router",
    "categories_router",
    "recurring_bills_router",
    "expenses_router",
    "incomes_router",
    "goals_router",
]