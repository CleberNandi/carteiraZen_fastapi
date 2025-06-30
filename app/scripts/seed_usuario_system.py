from app.core.config import config
from app.crud.user import create_user, get_user_by_email
from app.db.session import SessionLocal
from app.schemas.user import UserCreate


def seed_usuario_system() -> None:
    db = SessionLocal()
    exists = get_user_by_email(db, "system@system.dev")
    if not exists:
        user = create_user(
            db,
            UserCreate(
                name="system",
                email="system@system.dev",
                hashed_password=config.PASSWORD_SYSTEM,
            ),
            user_id=None,
        )
        print(f"Usuário system criado com id={user.id}")
    else:
        print("Usuário system já existe.")
    db.close()


if __name__ == "__main__":
    seed_usuario_system()
