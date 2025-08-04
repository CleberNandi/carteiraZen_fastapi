import enum

from sqlalchemy import (
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


class Conta(Base, AuditMixin):
    __tablename__ = "contas"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    agencia: Mapped[str] = mapped_column(String(20), nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    saldo_inicial: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("0.0"))  # type: ignore
    tipo: Mapped[TipoContaEnum] = mapped_column(
        Enum(TipoContaEnum), nullable=False, default=TipoContaEnum.corrente
    )

    user = relationship("User")
