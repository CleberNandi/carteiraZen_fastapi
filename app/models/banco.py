from sqlalchemy import Boolean, Column, Integer, String

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
