from app.db.session import SessionLocal
from app.models.user import User
from app.scripts.seed_bancos import seed_bancos
from app.scripts.seed_usuario_system import seed_usuario_system


def seed_all() -> None:
    seed_usuario_system()
    db = SessionLocal()
    user = db.query(User).filter(User.email == "system@system.local").first()
    db.close()
    system_id = getattr(user, "id", None)
    if not isinstance(system_id, int):
        system_id = None
    seed_bancos(user_id=system_id)
    print("Seed completo executado com sucesso!")


if __name__ == "__main__":
    seed_all()
