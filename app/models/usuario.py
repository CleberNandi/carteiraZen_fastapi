from typing import List, Optional

from sqlalchemy import TIMESTAMP, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hashed: Mapped[str] = mapped_column(String(255), nullable=False)
    totp_secret: Mapped[Optional[str]] = mapped_column(String(255))
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    plan: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[TIMESTAMP]] = mapped_column(TIMESTAMP, nullable=True)
    deleted_at: Mapped[Optional[TIMESTAMP]] = mapped_column(TIMESTAMP, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relacionamentos
    contas: Mapped[List["Conta"]] = relationship(  # noqa: F821 # type: ignore
        "Conta", back_populates="usuario", cascade="all, delete-orphan"
    )
    categorias: Mapped[List["Categoria"]] = relationship(  # noqa: F821 # type: ignore
        "Categoria", back_populates="usuario", cascade="all, delete-orphan"
    )
    sub_categorias: Mapped[List["SubCategoria"]] = relationship(  # noqa: F821 # type: ignore
        "SubCategoria", back_populates="usuario", cascade="all, delete-orphan"
    )
    cartoes: Mapped[List["Cartao"]] = relationship(  # noqa: F821 # type: ignore
        "Cartao", back_populates="usuario", cascade="all, delete-orphan"
    )
    faturas: Mapped[List["Fatura"]] = relationship(  # noqa: F821 # type: ignore
        "Fatura", back_populates="usuario", cascade="all, delete-orphan"
    )
    transacoes: Mapped[List["Transacao"]] = relationship(  # noqa: F821 # type: ignore
        "Transacao", back_populates="usuario", cascade="all, delete-orphan"
    )
    transacoes_parcelas: Mapped[List["TransacaoParcela"]] = relationship(  # noqa: F821 # type: ignore
        "TransacaoParcela", back_populates="usuario", cascade="all, delete-orphan"
    )
