# em conftest.py
from collections.abc import Generator
import os
from typing import Any

from core.dependencies import get_current_user
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.user import User


@pytest.fixture()
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


@pytest.fixture()
def fake_user(db_session: Session) -> User:
    from app.core.security import get_password_hash
    from app.models.user import User

    user = User(
        name="Usuário Teste",
        email="teste@example.com",
        hashed_password=get_password_hash("senha123"),
        ativo=True,
        sync_enabled=True,
        sync_uuid="fake-uuid",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client_with_auth_override() -> Generator[TestClient]:
    # Mock do get_current_user para sempre retornar um usuário fake
    def override_get_current_user() -> User:
        return User(id=1, name="Test User", email="test@example.com")

    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
