from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.nfce import NFCe


class NFCeItens(Base):
    __tablename__ = "nfce_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nota_id: Mapped[int] = mapped_column(ForeignKey("nfce.id", ondelete="CASCADE"))
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    unidade: Mapped[str] = mapped_column(String(20))
    valor_unitario: Mapped[float] = mapped_column(Numeric(10, 4))
    valor_total: Mapped[float] = mapped_column(Numeric(10, 2))

    nota: Mapped["NFCe"] = relationship("NFCe", back_populates="itens")
