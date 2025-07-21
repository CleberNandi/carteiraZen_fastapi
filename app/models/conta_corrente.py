import enum

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin


class TipoContaEnum(str, enum.Enum):
    corrente = "corrente"
    poupanca = "poupanca"


class ContaCorrente(Base, AuditMixin):
    __tablename__ = "contas_correntes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=True)
    digito: Mapped[str] = mapped_column(String(2), nullable=False)
    agencia_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agencias.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    saldo_inicial: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("0.0"))  # type: ignore
    tipo: Mapped[TipoContaEnum] = mapped_column(
        Enum(TipoContaEnum), nullable=False, default=TipoContaEnum.corrente
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    agencia = relationship("Agencia", back_populates="contas")
    user = relationship("User")
