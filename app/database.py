import os
import time
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

# Importar app.models garante que todas as classes table=True sejam registradas
import app.models  # noqa: F401

# Lê a URL de ambiente ou usa a conexão local padrão
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://finance_user:finance_password@localhost:5432/finance_db"
)

# Se estiver rodando de dentro do container Docker com docker compose,
# o host é "db", mas se rodar direto na sua máquina (ex: terminal/VSCode), o host é "localhost".
engine = create_engine(DATABASE_URL, echo=False)

def init_db(max_retries: int = 5, delay: int = 2):
    """
    Tenta conectar ao PostgreSQL e cria todas as tabelas se ainda não existirem.
    Possui retry para aguardar o tempo de boot do container do Postgres.
    """
    for attempt in range(1, max_retries + 1):
        try:
            SQLModel.metadata.create_all(engine)
            print("✅ Banco de dados e tabelas inicializados com sucesso!")
            return
        except OperationalError as e:
            if attempt == max_retries:
                print(f"❌ Erro ao conectar ao banco de dados: {e}")
                raise
            print(f"⏳ Aguardando banco de dados responder... ({attempt}/{max_retries})")
            time.sleep(delay)


def get_session():
    """Gerador de sessão para interagir com o banco."""
    with Session(engine) as session:
        yield session