from mixins.auditoria_mixins import AuditMixin
from mixins.sync_mixins import SyncMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Categoria(Base, AuditMixin, SyncMixin):
    __tablename__ = "categorias"

    descricao: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user = relationship("User")
