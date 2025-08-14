from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Fatura(Base):
    __tablename__ = "faturas"

    id: Mapped[int] = mapped_column(primary_key=True)
    valor_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    pago: Mapped[bool] = mapped_column(Boolean, default=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    fechamento: Mapped[Date] = mapped_column(Date, nullable=False)
    vencimento: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    conta_cartao_id: Mapped[int] = mapped_column(
        ForeignKey("cartoes.id"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    # Relacionamentos
    cartao: Mapped["Cartao"] = relationship(  # noqa: F821 # type: ignore
        "Cartao", back_populates="faturas"
    )
    usuario: Mapped["Usuario"] = relationship(  # noqa: F821 # type: ignore
        "Usuario", back_populates="faturas"
    )
    transacoes: Mapped["Transacao"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Transacao", back_populates="fatura", cascade="all, delete-orphan"
    )
