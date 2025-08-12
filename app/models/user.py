from datetime import datetime
import enum

from mixins.auditoria_mixins import AuditMixin
from mixins.sync_mixins import SyncMixin
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlanosEnum(str, enum.Enum):
    basic = "basic"
    premium = "premium"


class User(Base, AuditMixin, SyncMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(index=True, nullable=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(nullable=True, default=None)
    totp_secret: Mapped[str] = mapped_column(nullable=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_2fa_enabled: Mapped[bool] = mapped_column(default=False)
    plan: Mapped[str] = mapped_column(default=PlanosEnum.basic)
    is_email_confirmed: Mapped[bool] = mapped_column(default=False)
    email_confirmation_token: Mapped[str | None] = mapped_column(default=None)
    email_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
