from datetime import datetime

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from app.crud import user as user_crud
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.services.usuarios import UsuarioService

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    # Cria e limpa as tabelas antes e depois de cada teste
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    with engine.begin() as conn:
        for table in ["users", "auditoria"]:
            if table in Base.metadata.tables:
                conn.execute(Base.metadata.tables[table].delete())


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
        session.rollback()  # Limpa alterações após cada teste
    finally:
        session.close()


@pytest.fixture()
def usuario_service(db_session):
    return UsuarioService(db_session)


def test_deletar_usuario_com_sucesso(usuario_service, fake_user):
    user_id = fake_user.id
    executor_id = 999

    resultado = usuario_service.deletar(user_id=user_id, executor_id=executor_id)
    assert resultado is True

    # Verificar soft delete pelo service (deve retornar None)
    usuario = usuario_service.buscar_por_id(user_id)
    assert usuario is None

    # Verificar diretamente no banco os campos de soft delete
    user_db = user_crud.get_user(usuario_service.db, user_id)
    assert user_db.deleted_at is not None
    assert isinstance(user_db.deleted_at, datetime)
    assert user_db.deleted_by == executor_id
    assert user_db.ativo is False


def test_deletar_usuario_inexistente_gera_erro(usuario_service):
    with pytest.raises(HTTPException) as exc_info:
        usuario_service.deletar(user_id=999999, executor_id=1)
    assert exc_info.value.status_code == 404
    assert "Usuário não encontrado" in exc_info.value.detail


def test_create_first_user_without_user_id(client_with_auth_override):
    data = {
        "name": "Primeiro",
        "email": "primeiro@example.com",
        "hashed_password": "hash123",
        "totp_secret": None,
        "ativo": True,
        "is_superuser": True,
        "is_2fa_enabled": False,
        "plan": "free",
        "sync_enabled": True,
    }
    resp = test_create_first_user_without_user_id.post("/api/v1/users/", json=data)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Primeiro"
    assert resp.json()["email"] == "primeiro@example.com"
    assert "id" in resp.json()


def test_create_second_user_requires_user_id():
    client.post(
        "/api/v1/users/",
        json={
            "name": "Primeiro",
            "email": "primeiro@example.com",
            "hashed_password": "hash123",
            "ativo": True,
            "is_superuser": True,
            "is_2fa_enabled": False,
            "plan": "free",
            "sync_enabled": True,
        },
    )
    data = {
        "name": "Segundo",
        "email": "segundo@example.com",
        "hashed_password": "hash123",
        "ativo": True,
        "is_superuser": True,
        "is_2fa_enabled": False,
        "plan": "free",
        "sync_enabled": True,
    }
    resp = client.post("/api/v1/users/", json=data)
    assert resp.status_code == 400
    assert (
        "Usuário administrador" in resp.json()["detail"]
        or "user_id" in resp.json()["detail"]
    )


def test_create_user_with_user_id():
    client.post(
        "/api/v1/users/",
        json={
            "name": "Primeiro",
            "email": "primeiro@example.com",
            "hashed_password": "hash123",
            "ativo": True,
            "is_superuser": True,
            "is_2fa_enabled": False,
            "plan": "free",
            "sync_enabled": True,
        },
    )
    data = {
        "name": "Segundo",
        "email": "segundo@example.com",
        "hashed_password": "hash123",
        "ativo": True,
        "is_superuser": True,
        "is_2fa_enabled": False,
        "plan": "free",
        "sync_enabled": True,
    }
    # Atenção: se sua rota espera user_id no header ou token, ajuste aqui!
    resp = client.post("/api/v1/users/?user_id=1", json=data)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Segundo"
    assert resp.json()["email"] == "segundo@example.com"
    assert "id" in resp.json()


def test_update_user_auditoria():
    resp = client.post(
        "/api/v1/users/",
        json={
            "name": "Primeiro",
            "email": "primeiro@example.com",
            "hashed_password": "hash123",
            "totp_secret": None,
            "ativo": True,
            "is_superuser": True,
            "is_2fa_enabled": False,
            "plan": "free",
            "sync_enabled": True,
        },
    )
    user_id = resp.json()["id"]
    update_data = {
        "name": "Primeiro Atualizado",
        "email": "primeiro@example.com",
        "hashed_password": "hash123",
        "totp_secret": None,
        "ativo": True,
        "is_superuser": True,
        "is_2fa_enabled": False,
        "plan": "free",
        "sync_enabled": True,
    }
    resp = client.put(f"/api/v1/users/{user_id}?executor_id=2", json=update_data)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Primeiro Atualizado"

    # Verifica auditoria via endpoint (assumindo que exista)
    aud_resp = client.get("/api/v1/auditoria/?tabela=users&acao=update")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "users" and aud["acao"] == "update" for aud in auditorias
    )


def test_delete_user_auditoria():
    resp = client.post(
        "/api/v1/users/",
        json={
            "name": "Primeiro",
            "email": "primeiro@example.com",
            "hashed_password": "hash123",
            "ativo": True,
            "is_superuser": True,
            "is_2fa_enabled": False,
            "plan": "free",
            "sync_enabled": True,
        },
    )
    user_id = resp.json()["id"]
    resp = client.delete(f"/api/v1/users/{user_id}?executor_id=3")
    assert resp.status_code == 200

    aud_resp = client.get("/api/v1/auditoria/?tabela=users&acao=delete")
    assert aud_resp.status_code == 200
    auditorias = aud_resp.json()
    assert any(
        aud["tabela"] == "users" and aud["acao"] == "delete" for aud in auditorias
    )
