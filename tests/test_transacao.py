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
        for table in ["transacoes", "auditoria"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_create_transacao():
    data = {
        "descricao": "Compra supermercado",
        "valor": 150.0,
        "data": "2024-06-30",
        "tipo": "entrada",
        "categoria_id": 1,
        "conta_origem_id": 1,
        "forma_pagamento": "cartao_credito",
        "fatura_id": 1,
        "user_id": 1,
        "ativo": True,
    }
    resp = client.post("/api/v1/transacoes/?user_id=1", json=data)
    assert resp.status_code == 201
    assert resp.json()["descricao"] == "Compra supermercado"
    assert "id" in resp.json()


def test_update_transacao():
    data = {
        "descricao": "Compra supermercado",
        "valor": 150.0,
        "data": "2024-06-30",
        "tipo": "entrada",
        "categoria_id": 1,
        "conta_origem_id": 1,
        "forma_pagamento": "cartao_credito",
        "fatura_id": 1,
        "user_id": 1,
        "ativo": True,
    }
    resp = client.post("/api/v1/transacoes/?user_id=1", json=data)
    assert resp.status_code == 201, f"Failed to create transacao: {resp.json()}"
    transacao_id = resp.json().get("id")
    assert transacao_id is not None, f"Response JSON missing 'id': {resp.json()}"
    update_data = {
        "descricao": "Compra mercado atualizado",
        "valor": 200.0,
        "data": "2024-07-01",
        "tipo": "entrada",
        "categoria_id": 1,
        "conta_origem_id": 1,
        "forma_pagamento": "cartao_credito",
        "fatura_id": 1,
        "user_id": 1,
        "ativo": False,
    }
    resp = client.put(
        f"/api/v1/transacoes/{transacao_id}?executor_id=1", json=update_data
    )
    assert resp.status_code == 200
    assert resp.json()["descricao"] == "Compra mercado atualizado"


def test_delete_transacao():
    data = {
        "descricao": "Compra supermercado",
        "valor": 150.0,
        "data": "2024-06-30",
        "tipo": "entrada",
        "categoria_id": 1,
        "conta_origem_id": 1,
        "forma_pagamento": "cartao_credito",
        "fatura_id": 1,
        "user_id": 1,
        "ativo": True,
    }
    resp = client.post("/api/v1/transacoes/?user_id=1", json=data)
    assert resp.status_code == 201, f"Failed to create transacao: {resp.json()}"
    transacao_id = resp.json().get("id")
    assert transacao_id is not None, f"Response JSON missing 'id': {resp.json()}"
    resp = client.delete(f"/api/v1/transacoes/{transacao_id}?executor_id=1")
    assert resp.status_code == 204


def test_get_transacoes_list():
    client.post(
        "/api/v1/transacoes/?user_id=1",
        json={
            "descricao": "T1",
            "valor": 100,
            "data": "2024-06-30",
            "tipo": "entrada",
            "categoria_id": 1,
            "conta_origem_id": 1,
            "forma_pagamento": "cartao_credito",
            "fatura_id": 1,
            "user_id": 1,
            "ativo": True,
        },
    )
    client.post(
        "/api/v1/transacoes/?user_id=1",
        json={
            "descricao": "T2",
            "valor": 100,
            "data": "2024-06-30",
            "tipo": "entrada",
            "categoria_id": 1,
            "conta_origem_id": 1,
            "forma_pagamento": "cartao_credito",
            "fatura_id": 1,
            "user_id": 1,
            "ativo": True,
        },
    )
    client.post(
        "/api/v1/transacoes/?user_id=1",
        json={
            "descricao": "T3",
            "valor": 100,
            "data": "2024-06-30",
            "tipo": "entrada",
            "categoria_id": 1,
            "conta_origem_id": 1,
            "forma_pagamento": "cartao_credito",
            "fatura_id": 1,
            "user_id": 1,
            "ativo": True,
        },
    )
    resp = client.get("/api/v1/transacoes/")
    assert resp.status_code == 200
    transacoes: list[Any] = resp.json()
    assert isinstance(transacoes, list)
    assert len(transacoes) >= 2


def test_get_transacao_by_id():
    resp = client.post(
        "/api/v1/transacoes/?user_id=1",
        json={
            "descricao": "T1",
            "valor": 100,
            "data": "2024-06-30",
            "tipo": "entrada",
            "categoria_id": 1,
            "conta_origem_id": 1,
            "forma_pagamento": "cartao_credito",
            "fatura_id": 1,
            "user_id": 1,
            "ativo": True,
        },
    )
    transacao_id = resp.json()["id"]
    resp = client.get(f"/api/v1/transacoes/{transacao_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == transacao_id


def test_create_transacao_invalid_data():
    data = {
        "valor": 150.0,
        "data": "2024-06-30",
        "conta_corrente_id": 1,
        "categoria_id": 1,
        "cartao_id": 1,
        "ativo": True,
    }
    resp = client.post("/api/v1/transacoes/?user_id=1", json=data)
    assert resp.status_code == 422


def test_update_transacao_not_found():
    update_data = {
        "descricao": "Não Existe",
        "valor": 200.0,
        "data": "2024-07-01",
        "conta_corrente_id": 1,
        "categoria_id": 1,
        "cartao_id": 1,
        "ativo": False,
    }
    resp = client.put("/api/v1/transacoes/99999?executor_id=1", json=update_data)
    assert resp.status_code == 404


def test_delete_transacao_not_found():
    resp = client.delete("/api/v1/transacoes/99999?executor_id=1")
    assert resp.status_code == 404


def test_create_transacao_auditoria():
    data = {
        "descricao": "T1",
        "valor": 100,
        "data": "2024-06-30",
        "tipo": "entrada",
        "categoria_id": 1,
        "conta_origem_id": 1,
        "forma_pagamento": "cartao_credito",
        "fatura_id": 1,
        "user_id": 1,
        "ativo": True,
    }
    resp = client.post("/api/v1/transacoes/?user_id=1", json=data)
    assert resp.status_code == 201, f"Failed to create transacao: {resp.json()}"
    aud_resp = client.get("/api/v1/auditoria/?tabela=transacoes&acao=create")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "transacoes" and aud["acao"] == "create" for aud in auditorias
    )
