from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class Mixins:
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    ativo: Mapped[bool] = mapped_column(default=True)
    origin: Mapped[str] = mapped_column(default="api", nullable=False)
