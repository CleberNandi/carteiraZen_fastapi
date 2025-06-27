import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
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
