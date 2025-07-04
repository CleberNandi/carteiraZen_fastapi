from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FaturaCartaoCredito(Base):
    __tablename__ = "faturas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cartao_id: Mapped[int] = mapped_column(ForeignKey("cartoes.id"))
    mes: Mapped[int] = mapped_column()
    ano: Mapped[int] = mapped_column()
    valor_total: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str] = mapped_column(default="aberta")  # aberta, fechada, paga
    ativo: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    created_by: Mapped[int] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
    updated_by: Mapped[int] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)
    deleted_by: Mapped[int] = mapped_column(nullable=True)

    cartao = relationship("Cartao")
    transacoes = relationship("Transacao", back_populates="fatura")
    user = relationship("User")
