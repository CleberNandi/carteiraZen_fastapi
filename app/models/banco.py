from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from app.db.base import Base


class Banco(Base):
    __tablename__ = "bancos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, unique=True, index=True)
    codigo = Column(String, nullable=False, unique=True, index=True)
    ispb = Column(String, nullable=True, unique=True, index=True)
    cnpj = Column(String, nullable=True, unique=True, index=True)
    site = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    # Auditoria
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
