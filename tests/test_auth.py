from fastapi.testclient import TestClient
import pyotp
import pytest

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from tests.factories import create_user_with_2fa, create_user_without_2fa

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    with engine.begin() as conn:
        for table in ["users"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_login_user_without_2fa():
    db = SessionLocal()
    user = create_user_without_2fa(db)

    response = client.post(
        "/api/v1/login", json={"email": user.email, "password": "senha123"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_user_with_2fa():
    db = SessionLocal()
    user = create_user_with_2fa(db)

    totp = pyotp.TOTP(user.totp_secret)
    token_2fa = totp.now()

    response = client.post(
        "/api/v1/login",
        json={"email": user.email, "password": "senha123", "totp_token": token_2fa},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    response = client.post(
        "/api/v1/login", json={"email": "user@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_login_missing_fields():
    response = client.post("/api/v1/login", json={"email": "user@example.com"})
    assert response.status_code == 422


def test_login_2fa_invalid_token():
    db = SessionLocal()
    user = create_user_with_2fa(db)

    response = client.post(
        "/api/v1/login",
        json={"email": user.email, "password": "senha123", "totp_token": "000000"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token 2FA inválido"
