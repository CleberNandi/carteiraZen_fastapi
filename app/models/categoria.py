from mixins.mixins import Mixins
from mixins.sync_mixins import SyncMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Categoria(Base, Mixins, SyncMixin):
    __tablename__ = "categorias"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="categorias")  # type: ignore[name-defined]  # noqa: F821
    transacoes: Mapped[list["Transacao"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Transacao", back_populates="categoria", cascade="all, delete-orphan"
    )
    sub_categorias: Mapped[list["SubCategoria"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="categoria"
    )
