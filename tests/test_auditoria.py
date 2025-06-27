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
