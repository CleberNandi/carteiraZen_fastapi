import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class TipoContaEnum(str, enum.Enum):
    corrente = "corrente"
    poupanca = "poupanca"


class ContaCorrente(Base):
    __tablename__ = "contas_correntes"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False)
    digito = Column(String(2), nullable=True)
    agencia_id = Column(Integer, ForeignKey("agencias.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    saldo_inicial = Column(Float, nullable=False, server_default=text("0.0"))  # type: ignore
    tipo = Column(Enum(TipoContaEnum), nullable=False, default=TipoContaEnum.corrente)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)

    agencia = relationship("Agencia", back_populates="contas")
    user = relationship("User")
