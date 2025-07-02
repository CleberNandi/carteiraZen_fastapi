import pyotp
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from tests.factories import create_user_with_2fa, create_user_without_2fa

client = TestClient(app)


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
