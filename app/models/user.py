from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class User(Base, AuditMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(nullable=True)
    totp_secret: Mapped[str] = mapped_column(nullable=True)
    ativo: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_2fa_enabled: Mapped[bool] = mapped_column(default=False)
    plan: Mapped[str] = mapped_column(default="basic")
    sync_enabled: Mapped[bool] = mapped_column(default=False)
