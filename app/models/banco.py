from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin


class Banco(Base, AuditMixin):
    __tablename__ = "bancos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    codigo: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    ispb: Mapped[str] = mapped_column(nullable=True, unique=True, index=True)
    cnpj: Mapped[str] = mapped_column(nullable=True, unique=True, index=True)
    site: Mapped[str] = mapped_column(nullable=True)
    ativo: Mapped[bool] = mapped_column(default=True)

    agencias = relationship("Agencia", back_populates="banco")
