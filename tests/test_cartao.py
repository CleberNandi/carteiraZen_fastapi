import pytest
from fastapi.testclient import TestClient

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
