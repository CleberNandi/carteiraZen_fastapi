import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # type: ignore # noqa: F401  # Importa todos os models para registrar no metadata
from app.db.base import Base

SQLALCHEMY_DATABASE_URL = (
    "sqlite:///:memory:"
    if os.getenv("PYTEST_CURRENT_TEST")
    else os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
    if "sqlite" in SQLALCHEMY_DATABASE_URL
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
