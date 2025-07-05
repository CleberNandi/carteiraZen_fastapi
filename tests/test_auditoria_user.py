import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app
from tests.factories import user_data

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Limpa as tabelas após cada teste
    with engine.begin() as conn:
        for table in ["auditoria", "users"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


def test_auditoria_log_user_update():
    # Cria usuário
    resp = client.post("/api/v1/users/?user_id=1", json=user_data())
    user_id = resp.json()["id"]
    # Atualiza usuário
    update_data = {
        "name": "User Atualizado",
        "email": "auditado@example.com",
        "hashed_password": "hash123",
        "totp_secret": None,
        "is_active": True,
        "is_superuser": True,
        "is_2fa_enabled": False,
    }
    client.put(f"/api/v1/users/{user_id}?executor_id=2", json=update_data)
    # Consulta auditoria
    resp = client.get("/api/v1/auditoria/?tabela=users&acao=update")
    assert resp.status_code == 200
    auditorias = resp.json()
    assert any(
        aud["tabela"] == "users" and aud["acao"] == "update" for aud in auditorias
    )


def test_auditoria_log_user_delete():
    # Cria usuário
    resp = client.post("/api/v1/users/?user_id=1", json=user_data())
    user_id = resp.json()["id"]
    # Deleta usuário
    client.delete(f"/api/v1/users/{user_id}?executor_id=3")
    # Consulta auditoria
    resp = client.get("/api/v1/auditoria/?tabela=users&acao=delete")
    assert resp.status_code == 200
    auditorias = resp.json()
    assert any(
        aud["tabela"] == "users" and aud["acao"] == "delete" for aud in auditorias
    )
