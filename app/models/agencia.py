from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Agencia(Base):
    __tablename__ = "agencias"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), nullable=False)
    digito = Column(String(2), nullable=True)
    banco_id = Column(Integer, ForeignKey("bancos.id"), nullable=False)
    nome = Column(String(100), nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)

    banco = relationship("Banco", back_populates="agencias")
    contas = relationship("ContaCorrente", back_populates="agencia")
