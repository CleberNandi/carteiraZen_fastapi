from datetime import UTC, datetime

from core.security import gerar_totp_secret, get_password_hash
from fastapi import HTTPException
import pyotp
from sqlalchemy.orm import Session
from utils.auditoria_utils import registrar_auditoria, serialize_mapped
from utils.model_utils import apply_update_fields

from app import models
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserOut

Auditoria = models.Auditoria


class UserCreationRequiresUserIdError(Exception):
    pass


class UsuarioService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, skip: int = 0, limit: int = 10) -> list[UserOut]:
        usuarios = user_crud.get_users(self.db, skip, limit)
        return [UserOut.model_validate(u) for u in usuarios]

    def buscar_por_id(self, user_id: int) -> UserOut | None:
        usuario = user_crud.get_user(self.db, user_id)
        return UserOut.model_validate(usuario) if usuario else None

    def buscar_por_email(self, email: str) -> UserOut | None:
        usuario = user_crud.get_user_by_email(self.db, email)
        return UserOut.model_validate(usuario) if usuario else None

    def criar(self, dados: UserCreate, executor_id: int = 0) -> UserOut:
        total_users = self.db.query(user_crud.User).count()
        print("total_users: ", total_users)
        if total_users > 0 and executor_id == 0:
            raise HTTPException(
                status_code=400,
                detail="Não é possível criar usuários sem um usuário administrador",
            )
        if not dados.hashed_password:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        # Hash da senha e UUID de sync
        dados.hashed_password = get_password_hash(dados.hashed_password)

        # Criar usuário
        db_user = user_crud.create_user(self.db, dados, executor_id)

        # Auditoria
        auditoria = Auditoria(
            tabela="users",
            registro_id=db_user.id,
            acao="create",
            user_id=executor_id,
            dados_depois=str(dados.model_dump()),
        )
        self.db.add(auditoria)
        self.db.commit()
        self.db.refresh(db_user)
        return UserOut.model_validate(db_user)

    def atualizar(
        self, user_id: int, user_data: UserCreate, executor_id: int
    ) -> UserOut:
        user = user_crud.get_user(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        dados_antes = serialize_mapped(user)  # snapshot antes da alteração

        campos_alterados = apply_update_fields(
            model=user,
            data=user_data,
            fields=[
                "name",
                "email",
                "hashed_password",
                "is_active",
                "is_superuser",
                "plan",
                "sync_enabled",
                "sync_uuid",
            ],
        )

        if not campos_alterados:
            return UserOut.model_validate(user)

        user.updated_by = user_id
        user.updated_at = datetime.now(UTC)

        # Hash da senha se estiver vindo
        if user_data.hashed_password:
            user.hashed_password = get_password_hash(user_data.hashed_password)

        # Auditoria
        registrar_auditoria(
            db=self.db,
            tabela="users",
            registro_id=user.id,
            acao="update",
            user_id=executor_id,
            dados_antes=dados_antes,
            dados_input=user_data.model_dump(exclude_none=False),
            dados_depois=serialize_mapped(user),
        )
        self.db.commit()
        self.db.refresh(user)
        return UserOut.model_validate(user)

    def deletar(self, user_id: int, executor_id: int) -> bool:
        user = user_crud.get_user(self.db, user_id)
        if not user or user.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        user.deleted_by = executor_id
        user.deleted_at = datetime.now(UTC)
        user.ativo = False

        user_crud.update_user(self.db, user)

        # Auditoria
        registrar_auditoria(
            db=self.db,
            tabela="users",
            registro_id=user.id,
            acao="delete",
            user_id=executor_id,
            dados_antes=serialize_mapped(user),
        )
        self.db.commit()
        return True

    def ativar_2fa(self, user_id: int) -> str:
        user = user_crud.get_user(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if not user.totp_secret:
            user.totp_secret = gerar_totp_secret()
        user.is_2fa_enabled = True
        self.db.commit()
        self.db.refresh(user)

        return pyotp.TOTP(user.totp_secret).provisioning_uri(
            name=user.email, issuer_name="CarteiraZen"
        )
