from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    tabela: Mapped[str] = mapped_column(nullable=False)
    registro_id: Mapped[int] = mapped_column(nullable=False)
    acao: Mapped[str] = mapped_column(nullable=False)  # 'create', 'update', 'delete'
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    data: Mapped[datetime] = mapped_column(server_default=func.now())
    dados_antes: Mapped[str] = mapped_column()  # Pode ser JSON/texto
    dados_depois: Mapped[str] = mapped_column()
