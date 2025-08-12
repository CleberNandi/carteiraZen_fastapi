from mixins.auditoria_mixins import AuditMixin
from mixins.sync_mixins import SyncMixin
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Banco(Base, AuditMixin, SyncMixin):
    __tablename__ = "bancos"

    nome: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    codigo: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    ispb: Mapped[str] = mapped_column(nullable=True)
    cnpj: Mapped[str] = mapped_column(nullable=True, unique=True, index=True)
    site: Mapped[str] = mapped_column(nullable=True)
