from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Cartao(Base, AuditMixin):
    __tablename__ = "cartoes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    nome_impresso: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    validade: Mapped[str] = mapped_column(nullable=False)
    bandeira: Mapped[str] = mapped_column(nullable=False)
    limite: Mapped[int] = mapped_column(
        nullable=False
    )  # Limite em centavos ou outra unidade
    banco_id: Mapped[int] = mapped_column(ForeignKey("bancos.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True)
