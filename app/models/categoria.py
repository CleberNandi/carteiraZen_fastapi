from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    descricao: Mapped[str] = mapped_column()
    ativo: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    created_by: Mapped[int] = mapped_column(nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )
    updated_by: Mapped[int] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    deleted_by: Mapped[int] = mapped_column(nullable=True)

    user = relationship("User")
