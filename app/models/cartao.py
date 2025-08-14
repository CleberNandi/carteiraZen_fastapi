from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Cartao(Base):
    __tablename__ = "cartoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(16), nullable=False)
    descricao: Mapped[str] = mapped_column(String(20), nullable=False)
    bandeira: Mapped[str] = mapped_column(String(20), nullable=False)
    limite_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    fechamento: Mapped[Date] = mapped_column(Date, nullable=False)
    vencimento: Mapped[Date] = mapped_column(Date, nullable=False)
    cartao_padrao: Mapped[bool] = mapped_column(Boolean, default=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    conta_id: Mapped[int] = mapped_column(ForeignKey("contas.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    # Relacionamentos
    faturas: Mapped[list["Fatura"]] = relationship(  # noqa: F821 # type: ignore
        "Fatura", back_populates="cartao", cascade="all, delete-orphan"
    )
    usuario: Mapped["Usuario"] = relationship(  # noqa: F821 # type: ignore
        "Usuario", back_populates="cartoes"
    )
    conta: Mapped["Conta"] = relationship(  # noqa: F821 # type: ignore
        "Conta", back_populates="cartoes"
    )
