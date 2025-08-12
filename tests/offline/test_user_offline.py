from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User

client = TestClient(app)


def test_user_sync_flow(db_session):
    # 1. Criar usuário localmente (simula usuário offline com sync_uuid e sync_enabled)
    user = User(
        name="Sync User",
        email="syncuser@example.com",
        hashed_password="hashedpass",
        sync_enabled=True,
        sync_uuid="uuid-sync-1234",
        ativo=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. Simular push para servidor: no teste, só confirmamos que o usuário existe e está marcado para sync
    assert user.sync_enabled is True
    assert user.sync_uuid == "uuid-sync-1234"

    # 3. Simular pull do servidor: aqui a ideia seria mockar a resposta do servidor
    # Por enquanto, vamos fazer uma atualização local para simular o pull:
    user.name = "Sync User Updated"
    db_session.commit()

    # 4. Confirmar que os dados foram atualizados localmente
    updated_user = db_session.query(User).filter(User.id == user.id).first()
    assert updated_user.name == "Sync User Updated"
