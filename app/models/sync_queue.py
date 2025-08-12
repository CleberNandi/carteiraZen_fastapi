from uuid import UUID

from mixins.auditoria_mixins import AuditMixin
from mixins.sync_mixins import SyncMixin
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SyncQueue(Base, AuditMixin, SyncMixin):
    __tablename__ = "sync_queue"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    device_id: Mapped[str] = mapped_column(Text, nullable=False)
    entidade: Mapped[str] = mapped_column(Text, nullable=False)

    acao: Mapped[str] = mapped_column(
        Text, nullable=False, comment="create | update | delete"
    )

    payload: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)

    status: Mapped[str] = mapped_column(
        Text, nullable=False, default="pendente", comment="pendente | processado | erro"
    )

    tentativa: Mapped[int] = mapped_column(default=0, nullable=False)

    user = relationship("User")
