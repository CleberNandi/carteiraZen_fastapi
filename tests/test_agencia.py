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
        for table in ["agencias", "auditoria"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_create_agencia():
    data = {"numero": "1234", "digito": "5", "banco_id": 1, "nome": "Agência Central"}
    resp = client.post("/api/v1/agencias/?user_id=1", json=data)
    assert resp.status_code == 200
    assert resp.json()["numero"] == "1234"
    assert resp.json()["nome"] == "Agência Central"
    assert "id" in resp.json()


def test_update_agencia_auditoria():
    data = {"numero": "1234", "digito": "5", "banco_id": 1, "nome": "Agência Central"}
    resp = client.post("/api/v1/agencias/?user_id=1", json=data)
    ag_id = resp.json()["id"]
    update_data = {
        "numero": "1234",
        "digito": "5",
        "banco_id": 1,
        "nome": "Agência Atualizada",
    }
    resp = client.put(f"/api/v1/agencias/{ag_id}?executor_id=1", json=update_data)
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Agência Atualizada"
    aud_resp = client.get("/api/v1/auditoria/?tabela=agencias&acao=update")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "agencias" and aud["acao"] == "update" for aud in auditorias
    )


def test_delete_agencia_auditoria():
    data = {"numero": "1234", "digito": "5", "banco_id": 1, "nome": "Agência Central"}
    resp = client.post("/api/v1/agencias/?user_id=1", json=data)
    ag_id = resp.json()["id"]
    resp = client.delete(f"/api/v1/agencias/{ag_id}?executor_id=1")
    assert resp.status_code == 200
    aud_resp = client.get("/api/v1/auditoria/?tabela=agencias&acao=delete")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "agencias" and aud["acao"] == "delete" for aud in auditorias
    )


def test_create_agencia_invalid_data():
    # Missing required field 'numero'
    data = {"digito": "5", "banco_id": 1, "nome": "Agência Inválida"}
    resp = client.post("/api/v1/agencias/?user_id=1", json=data)
    assert resp.status_code == 422


def test_update_agencia_not_found():
    update_data = {"numero": "9999", "digito": "9", "banco_id": 1, "nome": "Não Existe"}
    resp = client.put("/api/v1/agencias/99999?executor_id=1", json=update_data)
    assert resp.status_code == 404


def test_delete_agencia_not_found():
    resp = client.delete("/api/v1/agencias/99999?executor_id=1")
    assert resp.status_code == 404


def test_get_agencias_list():
    # Create two agencias
    client.post(
        "/api/v1/agencias/?user_id=1",
        json={"numero": "1111", "digito": "1", "banco_id": 1, "nome": "Ag1"},
    )
    client.post(
        "/api/v1/agencias/?user_id=1",
        json={"numero": "2222", "digito": "2", "banco_id": 1, "nome": "Ag2"},
    )
    resp = client.get("/api/v1/agencias/")
    assert resp.status_code == 200
    agencias: list[Any] = resp.json()
    assert isinstance(agencias, list)
    assert len(agencias) >= 2


def test_get_agencia_by_id():
    resp = client.post(
        "/api/v1/agencias/?user_id=1",
        json={"numero": "3333", "digito": "3", "banco_id": 1, "nome": "Ag3"},
    )
    ag_id = resp.json()["id"]
    resp = client.get(f"/api/v1/agencias/{ag_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == ag_id


def test_create_agencia_auditoria():
    data = {"numero": "4444", "digito": "4", "banco_id": 1, "nome": "Agência Auditoria"}
    resp = client.post("/api/v1/agencias/?user_id=1", json=data)
    assert resp.status_code == 200
    aud_resp = client.get("/api/v1/auditoria/?tabela=agencias&acao=create")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "agencias" and aud["acao"] == "create" for aud in auditorias
    )
