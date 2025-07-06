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
        for table in ["contas_correntes", "auditoria", "agencias", "users"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_create_conta_corrente():
    # Cria dependências mínimas: user e agencia
    client.post("/api/v1/users/", json={"name": "User", "email": "user@ex.com"})
    client.post(
        "/api/v1/agencias/?user_id=1",
        json={
            "numero": "1234",
            "digito": "5",
            "banco_id": 1,
            "nome": "Agência Central",
        },
    )
    data = {
        "numero": "9999",
        "digito": "1",
        "agencia_id": 1,
        "user_id": 1,
        "saldo_inicial": 100.0,
        "tipo": "corrente",
    }
    resp = client.post("/api/v1/contas-correntes/?user_id=1", json=data)
    assert resp.status_code == 200
    assert resp.json()["numero"] == "9999"
    assert resp.json()["saldo_inicial"] == 100.0
    assert "id" in resp.json()


def test_update_conta_corrente_auditoria():
    client.post("/api/v1/users/", json={"name": "User", "email": "user@ex.com"})
    client.post(
        "/api/v1/agencias/?user_id=1",
        json={
            "numero": "1234",
            "digito": "5",
            "banco_id": 1,
            "nome": "Agência Central",
        },
    )
    data = {
        "numero": "9999",
        "digito": "1",
        "agencia_id": 1,
        "user_id": 1,
        "saldo_inicial": 100.0,
        "tipo": "corrente",
    }
    resp = client.post("/api/v1/contas-correntes/?user_id=1", json=data)
    conta_id = resp.json()["id"]
    update_data = {
        "numero": "9999",
        "digito": "1",
        "agencia_id": 1,
        "user_id": 1,
        "saldo_inicial": 200.0,
        "tipo": "corrente",
    }
    resp = client.put(
        f"/api/v1/contas-correntes/{conta_id}?executor_id=1", json=update_data
    )
    assert resp.status_code == 200
    assert resp.json()["saldo_inicial"] == 200.0
    aud_resp = client.get("/api/v1/auditoria/?tabela=contas_correntes&acao=update")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "contas_correntes" and aud["acao"] == "update"
        for aud in auditorias
    )


def test_delete_conta_corrente_auditoria():
    client.post("/api/v1/users/", json={"name": "User", "email": "user@ex.com"})
    client.post(
        "/api/v1/agencias/?user_id=1",
        json={
            "numero": "1234",
            "digito": "5",
            "banco_id": 1,
            "nome": "Agência Central",
        },
    )
    data = {
        "numero": "9999",
        "digito": "1",
        "agencia_id": 1,
        "user_id": 1,
        "saldo_inicial": 100.0,
        "tipo": "corrente",
    }
    resp = client.post("/api/v1/contas-correntes/?user_id=1", json=data)
    conta_id = resp.json()["id"]
    resp = client.delete(f"/api/v1/contas-correntes/{conta_id}?executor_id=1")
    assert resp.status_code == 200
    aud_resp = client.get("/api/v1/auditoria/?tabela=contas_correntes&acao=delete")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "contas_correntes" and aud["acao"] == "delete"
        for aud in auditorias
    )


def test_create_conta_corrente_invalid_data():
    # Missing required field 'numero'
    data = {
        "digito": "1",
        "agencia_id": 1,
        "user_id": 1,
        "saldo_inicial": 100.0,
        "tipo": "corrente",
    }
    resp = client.post("/api/v1/contas-correntes/?user_id=1", json=data)
    assert resp.status_code == 422


def test_update_conta_corrente_not_found():
    update_data = {
        "numero": "9999",
        "digito": "1",
        "agencia_id": 1,
        "user_id": 1,
        "saldo_inicial": 200.0,
        "tipo": "corrente",
    }
    resp = client.put("/api/v1/contas-correntes/99999?executor_id=1", json=update_data)
    assert resp.status_code == 404


def test_delete_conta_corrente_not_found():
    resp = client.delete("/api/v1/contas-correntes/99999?executor_id=1")
    assert resp.status_code == 404


def test_get_contas_correntes_list():
    client.post("/api/v1/users/", json={"name": "User", "email": "user@ex.com"})
    client.post(
        "/api/v1/agencias/?user_id=1",
        json={
            "numero": "1234",
            "digito": "5",
            "banco_id": 1,
            "nome": "Agência Central",
        },
    )
    client.post(
        "/api/v1/contas-correntes/?user_id=1",
        json={
            "numero": "1111",
            "digito": "1",
            "agencia_id": 1,
            "user_id": 1,
            "saldo_inicial": 100.0,
            "tipo": "corrente",
        },
    )
    client.post(
        "/api/v1/contas-correntes/?user_id=1",
        json={
            "numero": "2222",
            "digito": "2",
            "agencia_id": 1,
            "user_id": 1,
            "saldo_inicial": 200.0,
            "tipo": "corrente",
        },
    )
    resp = client.get("/api/v1/contas-correntes/")
    assert resp.status_code == 200
    contas = resp.json()
    assert isinstance(contas, list)
    assert len(contas) >= 2


def test_get_conta_corrente_by_id():
    client.post("/api/v1/users/", json={"name": "User", "email": "user@ex.com"})
    client.post(
        "/api/v1/agencias/?user_id=1",
        json={
            "numero": "1234",
            "digito": "5",
            "banco_id": 1,
            "nome": "Agência Central",
        },
    )
    resp = client.post(
        "/api/v1/contas-correntes/?user_id=1",
        json={
            "numero": "3333",
            "digito": "3",
            "agencia_id": 1,
            "user_id": 1,
            "saldo_inicial": 300.0,
            "tipo": "corrente",
        },
    )
    conta_id = resp.json()["id"]
    resp = client.get(f"/api/v1/contas-correntes/{conta_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == conta_id


def test_create_conta_corrente_auditoria():
    client.post("/api/v1/users/", json={"name": "User", "email": "user@ex.com"})
    client.post(
        "/api/v1/agencias/?user_id=1",
        json={
            "numero": "1234",
            "digito": "5",
            "banco_id": 1,
            "nome": "Agência Central",
        },
    )
    data = {
        "numero": "4444",
        "digito": "4",
        "agencia_id": 1,
        "user_id": 1,
        "saldo_inicial": 400.0,
        "tipo": "corrente",
    }
    resp = client.post("/api/v1/contas-correntes/?user_id=1", json=data)
    assert resp.status_code == 200
    aud_resp = client.get("/api/v1/auditoria/?tabela=contas_correntes&acao=create")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "contas_correntes" and aud["acao"] == "create"
        for aud in auditorias
    )
