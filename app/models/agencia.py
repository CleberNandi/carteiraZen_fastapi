from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin


class Agencia(Base, AuditMixin):
    __tablename__ = "agencias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(nullable=False)
    digito: Mapped[str] = mapped_column(nullable=True)
    banco_id: Mapped[str] = mapped_column(ForeignKey("bancos.id"), nullable=False)
    nome: Mapped[str] = mapped_column(nullable=True)
    ativo: Mapped[bool] = mapped_column(default=True)

    banco = relationship("Banco", back_populates="agencias")
    contas = relationship("ContaCorrente", back_populates="agencia")
