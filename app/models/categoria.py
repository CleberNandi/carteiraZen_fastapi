from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

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
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="categorias")  # type: ignore[name-defined]  # noqa: F821
    transacoes: Mapped[list["Transacao"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Transacao", back_populates="categoria", cascade="all, delete-orphan"
    )
    sub_categorias: Mapped[list["SubCategoria"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="categoria"
    )
