# app/models/mixins.py
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now(), nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)
    created_by: Mapped[int] = mapped_column(nullable=True)
    updated_by: Mapped[int] = mapped_column(nullable=True)
    deleted_by: Mapped[int] = mapped_column(nullable=True)
