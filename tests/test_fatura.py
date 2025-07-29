from typing import Any

from fastapi.testclient import TestClient
from models.base import Base
import pytest

from app.db.session import engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    with engine.begin() as conn:
        for table in ["faturas", "auditoria"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_create_fatura():
    data = {
        "cartao_id": 1,
        "mes": 12,
        "ano": 2024,
        "valor_total": 1000.0,
        "status": "open",
        "ativo": True,
        "user_id": 1,
    }
    resp = client.post("/api/v1/faturas/?user_id=1", json=data)
    assert resp.status_code == 201
    assert resp.json()["mes"] == 12
    assert "id" in resp.json()


def test_update_fatura():
    data = {
        "cartao_id": 1,
        "mes": 12,
        "ano": 2024,
        "valor_total": 1000.0,
        "status": "open",
        "ativo": True,
        "user_id": 1,
    }
    resp = client.post("/api/v1/faturas/?user_id=1", json=data)
    fatura_id = resp.json()["id"]
    update_data = {
        "mes": 1,
        "ano": 2025,
        "valor_total": 2000.0,
        "status": "closed",
        "ativo": False,
    }
    resp = client.put(f"/api/v1/faturas/{fatura_id}?executor_id=1", json=update_data)
    assert resp.status_code == 200
    assert resp.json()["mes"] == 1


def test_delete_fatura():
    data = {
        "cartao_id": 1,
        "mes": 12,
        "ano": 2024,
        "valor_total": 1000.0,
        "status": "open",
        "ativo": True,
        "user_id": 1,
    }
    resp = client.post("/api/v1/faturas/?user_id=1", json=data)
    fatura_id = resp.json()["id"]
    resp = client.delete(f"/api/v1/faturas/{fatura_id}?executor_id=1")
    assert resp.status_code == 204


def test_get_faturas_list():
    client.post(
        "/api/v1/faturas/?user_id=1",
        json={
            "cartao_id": 1,
            "mes": 11,
            "ano": 2024,
            "valor_total": 100,
            "status": "open",
            "ativo": True,
            "user_id": 1,
        },
    )
    client.post(
        "/api/v1/faturas/?user_id=1",
        json={
            "cartao_id": 1,
            "mes": 12,
            "ano": 2024,
            "valor_total": 200,
            "status": "open",
            "ativo": True,
            "user_id": 1,
        },
    )
    resp = client.get("/api/v1/faturas/")
    assert resp.status_code == 200
    faturas: list[Any] = resp.json()
    assert isinstance(faturas, list)
    assert len(faturas) >= 2


def test_get_fatura_by_id():
    resp = client.post(
        "/api/v1/faturas/?user_id=1",
        json={
            "cartao_id": 1,
            "mes": 12,
            "ano": 2024,
            "valor_total": 300,
            "status": "open",
            "ativo": True,
            "user_id": 1,
        },
    )
    fatura_id = resp.json()["id"]
    resp = client.get(f"/api/v1/faturas/{fatura_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == fatura_id


def test_create_fatura_invalid_data():
    data = {
        "mes": 12,
        "ano": 2024,
        "valor_total": 1000.0,
        "status": "open",
        "ativo": True,
        "user_id": 1,
    }
    resp = client.post("/api/v1/faturas/?user_id=1", json=data)
    assert resp.status_code == 422


def test_update_fatura_not_found():
    update_data = {
        "mes": 1,
        "ano": 2025,
        "valor_total": 2000.0,
        "status": "closed",
        "ativo": False,
    }
    resp = client.put("/api/v1/faturas/99999?executor_id=1", json=update_data)
    assert resp.status_code == 404


def test_delete_fatura_not_found():
    resp = client.delete("/api/v1/faturas/99999?executor_id=1")
    assert resp.status_code == 404


def test_create_fatura_auditoria():
    data = {
        "cartao_id": 1,
        "mes": 12,
        "ano": 2024,
        "valor_total": 4000.0,
        "status": "open",
        "ativo": True,
        "user_id": 1,
    }
    resp = client.post("/api/v1/faturas/?user_id=1", json=data)
    assert resp.status_code == 201
    aud_resp = client.get("/api/v1/auditoria/?tabela=faturas&acao=create")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "faturas" and aud["acao"] == "create" for aud in auditorias
    )
