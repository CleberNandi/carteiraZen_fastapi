from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, BigInteger, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Conta(Base):
    __tablename__ = "contas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    saldo_cents: Mapped[int] = mapped_column(BigInteger, default=0)
    cheque_especial_cents: Mapped[int] = mapped_column(BigInteger, default=0)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    incluir_na_soma_inicial: Mapped[bool] = mapped_column(Boolean, default=True)
    conta_padrao: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    banco_id: Mapped[int] = mapped_column(ForeignKey("bancos.id"), nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="contas") # type: ignore[name-defined]  # noqa: F821
    banco: Mapped["Banco"] = relationship(back_populates="contas") # type: ignore[name-defined]  # noqa: F821
    cartoes: Mapped[list["Cartao"]] = relationship(back_populates="conta") # type: ignore[name-defined]  # noqa: F821
