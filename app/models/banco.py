from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.conta import Conta


class Banco(Base):
    __tablename__ = "bancos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    codigo: Mapped[str] = mapped_column(String, nullable=False)
    ispb: Mapped[str | None] = mapped_column(String)
    cnpj: Mapped[str | None] = mapped_column(String)
    site: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)

    contas: Mapped[list[Conta]] = relationship(back_populates="banco")
