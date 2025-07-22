# em conftest.py
from collections.abc import Generator
import os
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine


@pytest.fixture(scope="function")
def db_session() -> Generator[Session]:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db() -> Generator[Any]:
    yield  # Isso permite que os testes sejam executados
    # Código para remover o banco de dados de teste
    if os.path.exists("sql_app_test.db"):
        os.remove("sql_app_test.db")
