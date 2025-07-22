from typing import Any

from fastapi.testclient import TestClient
import pytest

from app.db.base import Base
from app.db.session import engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Limpa as tabelas após cada teste
    with engine.begin() as conn:
        for table in ["bancos", "auditoria"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_create_banco():
    data = {
        "nome": "Banco Teste",
        "codigo": "999",
        "ispb": "12345678",
        "cnpj": "00.000.000/0001-91",
        "site": "https://bancoteste.com",
        "ativo": True,
    }
    response = client.post("/api/v1/bancos/?user_id=1", json=data)
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["nome"] == data["nome"]
    assert resp_json["codigo"] == data["codigo"]
    assert resp_json["ativo"] is True


def test_create_banco_duplicate_codigo():
    data = {"nome": "Banco Teste", "codigo": "999"}
    client.post("/api/v1/bancos/?user_id=1", json=data)
    response = client.post("/api/v1/bancos/?user_id=1", json=data)
    assert response.status_code == 400
    assert "cadastrado" in response.json()["detail"].lower()


def test_get_bancos():
    client.post("/api/v1/bancos/?user_id=1", json={"nome": "Banco 1", "codigo": "101"})
    client.post("/api/v1/bancos/?user_id=1", json={"nome": "Banco 2", "codigo": "102"})
    response = client.get("/api/v1/bancos/")
    assert response.status_code == 200
    bancos: list[Any] = response.json()
    assert isinstance(bancos, list)
    assert len(bancos) >= 2


def test_get_banco_not_found():
    response = client.get("/api/v1/bancos/99999")
    assert response.status_code == 404


def test_update_banco():
    resp = client.post(
        "/api/v1/bancos/?user_id=1", json={"nome": "Banco Atualiza", "codigo": "777"}
    )
    banco_id = resp.json()["id"]
    update_data = {"nome": "Banco Atualizado", "codigo": "777", "ativo": False}
    response = client.put(f"/api/v1/bancos/{banco_id}?user_id=1", json=update_data)
    assert response.status_code in (200, 204)
    get_resp = client.get(f"/api/v1/bancos/{banco_id}")
    assert get_resp.json()["nome"] == "Banco Atualizado"
    assert get_resp.json()["ativo"] is False


def test_delete_banco():
    resp = client.post(
        "/api/v1/bancos/?user_id=1", json={"nome": "Banco Deleta", "codigo": "555"}
    )
    banco_id = resp.json()["id"]
    response = client.delete(f"/api/v1/bancos/{banco_id}?user_id=1")
    assert response.status_code in (200, 204)
    get_resp = client.get(f"/api/v1/bancos/{banco_id}")
    assert get_resp.status_code == 404


def test_create_banco_invalid_data():
    # Missing required field 'nome'
    data = {"codigo": "000"}
    resp = client.post("/api/v1/bancos/?user_id=1", json=data)
    assert resp.status_code == 422


def test_update_banco_not_found():
    update_data = {"nome": "Não Existe", "codigo": "999"}
    resp = client.put("/api/v1/bancos/99999?user_id=1", json=update_data)
    assert resp.status_code == 404


def test_delete_banco_not_found():
    resp = client.delete("/api/v1/bancos/99999?user_id=1")
    assert resp.status_code == 404


def test_get_bancos_list():
    client.post("/api/v1/bancos/?user_id=1", json={"nome": "Banco 1", "codigo": "101"})
    client.post("/api/v1/bancos/?user_id=1", json={"nome": "Banco 2", "codigo": "102"})
    resp = client.get("/api/v1/bancos/")
    assert resp.status_code == 200
    bancos: list[Any] = resp.json()
    assert isinstance(bancos, list)
    assert len(bancos) >= 2


def test_get_banco_by_id():
    resp = client.post(
        "/api/v1/bancos/?user_id=1", json={"nome": "Banco Unico", "codigo": "888"}
    )
    banco_id = resp.json()["id"]
    resp = client.get(f"/api/v1/bancos/{banco_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == banco_id


def test_create_banco_auditoria():
    data = {"nome": "Banco Auditoria", "codigo": "777"}
    resp = client.post("/api/v1/bancos/?user_id=1", json=data)
    assert resp.status_code == 200
    aud_resp = client.get("/api/v1/auditoria/?tabela=bancos&acao=create")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "bancos" and aud["acao"] == "create" for aud in auditorias
    )
