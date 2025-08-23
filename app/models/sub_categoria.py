from mixins.sync_mixins import SyncMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.mixins.mixins import Mixins


class SubCategoria(Base, Mixins, SyncMixin):
    __tablename__ = "sub_categorias"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    categoria: Mapped["Categoria"] = relationship(back_populates="sub_categorias")  # type: ignore[name-defined]  # noqa: F821
    usuario: Mapped["Usuario"] = relationship(back_populates="sub_categorias")  # type: ignore[name-defined]  # noqa: F821
    transacoes: Mapped[list["Transacao"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Transacao", back_populates="sub_categoria", cascade="all, delete-orphan"
    )
