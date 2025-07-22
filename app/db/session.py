from collections.abc import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import config
from app.db.base import Base
import app.models  # type: ignore # noqa: F401  # Importa todos os models para registrar no metadata

SQLALCHEMY_DATABASE_URL = config.DATABASE_URL


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
    if "sqlite" in SQLALCHEMY_DATABASE_URL
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print(f"Ambiente ativo: {config.ENV}")
print(f"URL do banco: {config.DATABASE_URL}")


# Cria as tabelas no SQLite em memória durante os testes
def create_all_tables_for_test() -> None:
    if os.getenv("PYTEST_CURRENT_TEST"):
        Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


create_all_tables_for_test()
