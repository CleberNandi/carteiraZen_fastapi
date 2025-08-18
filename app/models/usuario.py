from datetime import UTC, datetime
from typing import TYPE_CHECKING

from mixins.mixins import Mixins
from mixins.sync_mixins import SyncMixin
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.auth_session import AuthSession
    from app.models.backup_code import BackupCode
    from app.models.cartao import Cartao
    from app.models.categoria import Categoria
    from app.models.conta import Conta
    from app.models.fatura import Fatura
    from app.models.sub_categoria import SubCategoria
    from app.models.transacao import Transacao
    from app.models.transacao_parcela import TransacaoParcela


class Usuario(Base, Mixins, SyncMixin):
    __tablename__ = "usuarios"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hashed: Mapped[str] = mapped_column(String(255), nullable=False)

    # Campos de 2FA
    totp_secret: Mapped[str | None] = mapped_column(String(255))
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Campos de segurança
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[str | None] = mapped_column(String(255))

    # Controle de login
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    # Plano
    plan: Mapped[str | None] = mapped_column(String(20))

    # Relacionamentos existentes
    contas: Mapped[list["Conta"]] = relationship(
        "Conta", back_populates="usuario", cascade="all, delete-orphan"
    )
    categorias: Mapped[list["Categoria"]] = relationship(
        "Categoria", back_populates="usuario", cascade="all, delete-orphan"
    )
    sub_categorias: Mapped[list["SubCategoria"]] = relationship(
        "SubCategoria", back_populates="usuario", cascade="all, delete-orphan"
    )
    cartoes: Mapped[list["Cartao"]] = relationship(
        "Cartao", back_populates="usuario", cascade="all, delete-orphan"
    )
    faturas: Mapped[list["Fatura"]] = relationship(
        "Fatura", back_populates="usuario", cascade="all, delete-orphan"
    )
    transacoes: Mapped[list["Transacao"]] = relationship(
        "Transacao", back_populates="usuario", cascade="all, delete-orphan"
    )
    transacoes_parcelas: Mapped[list["TransacaoParcela"]] = relationship(
        "TransacaoParcela", back_populates="usuario", cascade="all, delete-orphan"
    )

    # Novos relacionamentos de auth
    auth_sessions: Mapped[list["AuthSession"]] = relationship(
        "AuthSession", back_populates="usuario", cascade="all, delete-orphan"
    )
    backup_codes: Mapped[list["BackupCode"]] = relationship(
        "BackupCode", back_populates="usuario", cascade="all, delete-orphan"
    )

    @property
    def is_locked(self) -> bool:
        """Verifica se conta está bloqueada"""
        if not self.locked_until:
            return False
        return datetime.now(UTC) < self.locked_until

    def reset_failed_attempts(self) -> None:
        """Reseta tentativas de login falhadas"""
        self.failed_login_attempts = 0
        self.locked_until = None
