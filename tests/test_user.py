from fastapi.testclient import TestClient
from models.base import Base
import pytest

from app.db.session import engine
from app.main import app
from tests.factories import user_data, user_data_2

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Limpa as tabelas após cada teste
    with engine.begin() as conn:
        for table in ["users", "auditoria"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_create_first_user_without_user_id():
    data = user_data()
    resp = client.post("/api/v1/users/", json=data)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Primeiro"
    assert resp.json()["email"] == "primeiro@example.com"
    assert "id" in resp.json()


def test_create_second_user_requires_user_id():
    client.post("/api/v1/users/", json=user_data())
    data = user_data_2()
    resp = client.post("/api/v1/users/", json=data)
    assert resp.status_code == 400
    assert "user_id é obrigatório" in resp.json()["detail"]


def test_create_user_with_user_id():
    client.post("/api/v1/users/", json=user_data())
    data = user_data_2()
    resp = client.post("/api/v1/users/?user_id=1", json=data)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Segundo"
    assert resp.json()["email"] == "segundo@example.com"
    assert "id" in resp.json()


def test_update_user_auditoria():
    resp = client.post("/api/v1/users/", json=user_data())
    user_id = resp.json()["id"]
    update_data = {
        "name": "Primeiro Atualizado",
        "email": "primeiro@example.com",
        "hashed_password": "hash123",
        "totp_secret": None,
        "is_active": True,
        "is_superuser": True,
        "is_2fa_enabled": False,
    }
    resp = client.put(f"/api/v1/users/{user_id}?executor_id=2", json=update_data)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Primeiro Atualizado"
    # Verifica auditoria
    aud_resp = client.get("/api/v1/auditoria/?tabela=users&acao=update")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "users" and aud["acao"] == "update" for aud in auditorias
    )


def test_delete_user_auditoria():
    resp = client.post("/api/v1/users/", json=user_data())
    user_id = resp.json()["id"]
    resp = client.delete(f"/api/v1/users/{user_id}?executor_id=3")
    assert resp.status_code == 200
    # Verifica auditoria
    aud_resp = client.get("/api/v1/auditoria/?tabela=users&acao=delete")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "users" and aud["acao"] == "delete" for aud in auditorias
    )
