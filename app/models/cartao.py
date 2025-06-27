from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from app.db.base import Base


class Cartao(Base):
    __tablename__ = "cartoes"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, nullable=False, unique=True, index=True)
    nome_impresso = Column(String, nullable=False, unique=True, index=True)
    validade = Column(String, nullable=False)
    bandeira = Column(String, nullable=False)
    limite = Column(Integer, nullable=False)  # Limite em centavos ou outra unidade
    banco_id = Column(Integer, ForeignKey("bancos.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ativo = Column(Boolean, default=True)

    # Auditoria
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
