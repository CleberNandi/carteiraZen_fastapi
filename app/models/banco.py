from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Banco(Base, AuditMixin):
    __tablename__ = "bancos"

    nome: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    codigo: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    ispb: Mapped[str] = mapped_column(nullable=True)
    cnpj: Mapped[str] = mapped_column(nullable=True, unique=True, index=True)
    site: Mapped[str] = mapped_column(nullable=True)
