from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.mixins.mixins import Mixins


class Auditoria(Base, Mixins):
    __tablename__ = "auditoria"

    tabela: Mapped[str] = mapped_column(nullable=False)
    registro_id: Mapped[int] = mapped_column(nullable=False)
    acao: Mapped[str] = mapped_column(nullable=False)  # 'create', 'update', 'delete'
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )
    data: Mapped[datetime] = mapped_column(server_default=func.now())
    dados_antes: Mapped[str | None] = mapped_column(
        nullable=True
    )  # Pode ser JSON/texto
    dados_input: Mapped[str | None] = mapped_column(
        nullable=True
    )  # Pode ser JSON/texto
    dados_depois: Mapped[str | None] = mapped_column(nullable=True)
