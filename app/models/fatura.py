from mixins.auditoria_mixins import AuditMixin
from mixins.sync_mixins import SyncMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Fatura(Base, AuditMixin, SyncMixin):
    __tablename__ = "faturas"

    cartao_id: Mapped[int] = mapped_column(ForeignKey("cartoes.id"))
    mes: Mapped[int] = mapped_column()
    ano: Mapped[int] = mapped_column()
    valor_total: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str] = mapped_column(default="aberta")  # aberta, fechada, paga
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    cartao = relationship("Cartao")
    transacoes = relationship("Transacao", back_populates="fatura")
    user = relationship("User")
