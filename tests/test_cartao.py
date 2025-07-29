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
    # Limpa as tabelas após cada teste
    with engine.begin() as conn:
        for table in ["cartoes", "auditoria"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_create_cartao():
    data = {
        "numero": "1234-5678-9012-3456",
        "nome_impresso": "João da Silva",
        "validade": "2025-12",
        "bandeira": "Visa",
        "limite": 500000,  # Limite em centavos
        "banco_id": 1,
        "user_id": 1,
        "ativo": True,
    }
    resp = client.post("/api/v1/cartoes/?user_id=1", json=data)
    assert resp.status_code == 200
    assert resp.json()["numero"] == "1234-5678-9012-3456"
    assert resp.json()["nome_impresso"] == "João da Silva"
    assert "id" in resp.json()


def test_update_cartao_auditoria():
    data = {
        "numero": "1234-5678-9012-3456",
        "nome_impresso": "João da Silva",
        "validade": "2025-12",
        "bandeira": "Visa",
        "limite": 500000,  # Limite em centavos
        "banco_id": 1,
        "user_id": 1,
    }
    resp = client.post("/api/v1/cartoes/?user_id=1", json=data)
    cartao_id = resp.json()["id"]
    update_data = {
        "numero": "1234-4545-5656-3456",
        "nome_impresso": "Joao Gomes Apolinário",
        "validade": "string",
        "bandeira": "string",
        "limite": 0,
        "banco_id": 1,
        "user_id": 1,
    }
    resp = client.put(f"/api/v1/cartoes/{cartao_id}?executor_id=1", json=update_data)
    assert resp.status_code == 200
    assert resp.json()["nome_impresso"] == "Joao Gomes Apolinário"
    aud_resp = client.get("/api/v1/auditoria/?tabela=cartoes&acao=update")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "cartoes" and aud["acao"] == "update" for aud in auditorias
    )


def test_delete_agencia_auditoria():
    data = {
        "numero": "1234-4545-5656-3456",
        "nome_impresso": "Joao Gomes Apolinário",
        "validade": "string",
        "bandeira": "string",
        "limite": 0,
        "banco_id": 1,
        "user_id": 1,
    }
    resp = client.post("/api/v1/cartoes/?user_id=1", json=data)
    cartao_id = resp.json()["id"]
    resp = client.delete(f"/api/v1/cartoes/{cartao_id}?executor_id=1")
    assert resp.status_code == 200
    aud_resp = client.get("/api/v1/auditoria/?tabela=cartoes&acao=delete")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "cartoes" and aud["acao"] == "delete" for aud in auditorias
    )


def test_create_cartao_invalid_data():
    # Missing required field 'numero'
    data = {
        "nome_impresso": "Nome Inválido",
        "validade": "2025-12",
        "bandeira": "Visa",
        "limite": 100000,
        "banco_id": 1,
        "user_id": 1,
    }
    resp = client.post("/api/v1/cartoes/?user_id=1", json=data)
    assert resp.status_code == 422


def test_update_cartao_not_found():
    update_data = {
        "numero": "9999-9999-9999-9999",
        "nome_impresso": "Não Existe",
        "validade": "2025-12",
        "bandeira": "Visa",
        "limite": 100000,
        "banco_id": 1,
        "user_id": 1,
    }
    resp = client.put("/api/v1/cartoes/99999?executor_id=1", json=update_data)
    assert resp.status_code == 404


def test_delete_cartao_not_found():
    resp = client.delete("/api/v1/cartoes/99999?executor_id=1")
    assert resp.status_code == 404


def test_get_cartoes_list():
    # Create two cartoes
    client.post(
        "/api/v1/cartoes/?user_id=1",
        json={
            "numero": "1111-1111-1111-1111",
            "nome_impresso": "Cartao 1",
            "validade": "2025-12",
            "bandeira": "Visa",
            "limite": 100000,
            "banco_id": 1,
            "user_id": 1,
        },
    )
    client.post(
        "/api/v1/cartoes/?user_id=1",
        json={
            "numero": "2222-2222-2222-2222",
            "nome_impresso": "Cartao 2",
            "validade": "2025-12",
            "bandeira": "Visa",
            "limite": 200000,
            "banco_id": 1,
            "user_id": 1,
        },
    )
    resp = client.get("/api/v1/cartoes/")
    assert resp.status_code == 200
    cartoes: list[Any] = resp.json()
    assert isinstance(cartoes, list)
    assert len(cartoes) >= 2


def test_get_cartao_by_id():
    resp = client.post(
        "/api/v1/cartoes/?user_id=1",
        json={
            "numero": "3333-3333-3333-3333",
            "nome_impresso": "Cartao 3",
            "validade": "2025-12",
            "bandeira": "Visa",
            "limite": 300000,
            "banco_id": 1,
            "user_id": 1,
        },
    )
    cartao_id = resp.json()["id"]
    resp = client.get(f"/api/v1/cartoes/{cartao_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cartao_id


def test_create_cartao_auditoria():
    data = {
        "numero": "4444-4444-4444-4444",
        "nome_impresso": "Cartao Auditoria",
        "validade": "2025-12",
        "bandeira": "Visa",
        "limite": 400000,
        "banco_id": 1,
        "user_id": 1,
    }
    resp = client.post("/api/v1/cartoes/?user_id=1", json=data)
    assert resp.status_code == 200
    aud_resp = client.get("/api/v1/auditoria/?tabela=cartoes&acao=create")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "cartoes" and aud["acao"] == "create" for aud in auditorias
    )
