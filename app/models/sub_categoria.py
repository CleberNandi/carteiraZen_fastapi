from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SubCategoria(Base):
    __tablename__ = "sub_categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    categoria: Mapped["Categoria"] = relationship(back_populates="sub_categorias")  # type: ignore[name-defined]  # noqa: F821
    usuario: Mapped["Usuario"] = relationship(back_populates="sub_categorias")  # type: ignore[name-defined]  # noqa: F821
    transacoes: Mapped[list["Transacao"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Transacao", back_populates="sub_categoria", cascade="all, delete-orphan"
    )
