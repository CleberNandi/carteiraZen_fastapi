from __future__ import annotations

from typing import TYPE_CHECKING

from mixins.sync_mixins import SyncMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.mixins.mixins import Mixins

if TYPE_CHECKING:
    from app.models.conta import Conta


class Banco(Base, Mixins, SyncMixin):
    __tablename__ = "bancos"

    nome: Mapped[str] = mapped_column(String, nullable=False)
    codigo: Mapped[str] = mapped_column(String, nullable=False)
    ispb: Mapped[str | None] = mapped_column(String)
    cnpj: Mapped[str | None] = mapped_column(String)
    site: Mapped[str | None] = mapped_column(String)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)

    contas: Mapped[list[Conta]] = relationship(back_populates="banco")
