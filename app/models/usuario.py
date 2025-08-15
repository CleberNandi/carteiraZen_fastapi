from typing import TYPE_CHECKING

from mixins.mixins import Mixins
from mixins.sync_mixins import SyncMixin
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
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
    totp_secret: Mapped[str | None] = mapped_column(String(255))
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    plan: Mapped[str | None] = mapped_column(String(20))

    # Relacionamentos
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
