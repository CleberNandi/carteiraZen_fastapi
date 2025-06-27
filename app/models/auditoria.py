from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.db.base import Base


class Auditoria(Base):
    __tablename__ = "auditoria"
    id = Column(Integer, primary_key=True)
    tabela = Column(String, nullable=False)
    registro_id = Column(Integer, nullable=False)
    acao = Column(String, nullable=False)  # 'create', 'update', 'delete'
    user_id = Column(Integer, ForeignKey("users.id"))
    data = Column(DateTime, server_default=func.now())
    dados_antes = Column(String)  # Pode ser JSON/texto
    dados_depois = Column(String)
