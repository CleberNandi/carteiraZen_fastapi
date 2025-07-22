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
        for table in ["auditoria", "bancos", "users"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_auditoria_log_banco_create():
    # Cria um banco (gera auditoria)
    banco_data = {"nome": "Banco Auditado", "codigo": "1234"}
    client.post("/api/v1/bancos/?user_id=1", json=banco_data)
    # Consulta auditoria
    resp = client.get("/api/v1/auditoria/?tabela=bancos")
    assert resp.status_code == 200
    auditorias = resp.json()
    assert any(
        aud["tabela"] == "bancos" and aud["acao"] == "create" for aud in auditorias
    )


def test_auditoria_filtro_user():
    # Cria dois bancos com user_id diferentes
    client.post("/api/v1/bancos/?user_id=1", json={"nome": "Banco 1", "codigo": "u1"})
    client.post("/api/v1/bancos/?user_id=2", json={"nome": "Banco 2", "codigo": "u2"})
    # Consulta auditoria filtrando por user_id=2
    resp = client.get("/api/v1/auditoria/?user_id=2")
    assert resp.status_code == 200
    auditorias = resp.json()
    assert all(aud["user_id"] == 2 for aud in auditorias)


def test_auditoria_log_banco_update_delete():
    # Cria banco
    resp = client.post(
        "/api/v1/bancos/?user_id=1", json={"nome": "Banco Update", "codigo": "upd"}
    )
    banco_id = resp.json()["id"]
    # Atualiza banco
    client.put(
        f"/api/v1/bancos/{banco_id}?user_id=1",
        json={"nome": "Banco Atualizado", "codigo": "upd"},
    )
    # Deleta banco
    client.delete(f"/api/v1/bancos/{banco_id}?user_id=1")
    # Consulta auditoria para update e delete
    resp = client.get("/api/v1/auditoria/?tabela=bancos&acao=update")
    assert resp.status_code == 200
    auditorias = resp.json()
    assert any(aud["acao"] == "update" for aud in auditorias)
    resp = client.get("/api/v1/auditoria/?tabela=bancos&acao=delete")
    assert resp.status_code == 200
    auditorias = resp.json()
    assert any(aud["acao"] == "delete" for aud in auditorias)


def test_auditoria_invalid_filter():
    resp = client.get("/api/v1/auditoria/?acao=invalid")
    assert resp.status_code == 200
    auditorias: list[Any] = resp.json()
    # Expecting no results for invalid filter
    assert isinstance(auditorias, list)
    assert len(auditorias) == 0
