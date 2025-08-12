from mixins.auditoria_mixins import AuditMixin
from mixins.sync_mixins import SyncMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Cartao(Base, AuditMixin, SyncMixin):
    __tablename__ = "cartoes"

    numero: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    nome_impresso: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    validade: Mapped[str] = mapped_column(nullable=False)
    bandeira: Mapped[str] = mapped_column(nullable=False)
    limite: Mapped[int] = mapped_column(
        nullable=False
    )  # Limite em centavos ou outra unidade
    banco_id: Mapped[int] = mapped_column(ForeignKey("bancos.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
