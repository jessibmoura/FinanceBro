from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from app.database import init_db
from app.routers import (
    accounts_router,
    snapshots_router,
    categories_router,
    recurring_bills_router,
    expenses_router,
    incomes_router,
    goals_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Garante que as tabelas existem ao ligar a API
    init_db()
    yield


app = FastAPI(
    title="Personal Finance API",
    version="1.0.0",
    description="API de Gerenciamento Financeiro Pessoal",
    lifespan=lifespan,
)

os.makedirs("imgs", exist_ok=True)
app.mount("/imgs", StaticFiles(directory="imgs"), name="imgs")

# Registro dos roteadores individuais
app.include_router(accounts_router)
app.include_router(snapshots_router)
app.include_router(categories_router)
app.include_router(recurring_bills_router)
app.include_router(expenses_router)
app.include_router(incomes_router)
app.include_router(goals_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "Personal Finance API"}