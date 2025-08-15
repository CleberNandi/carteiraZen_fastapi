from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.nfce_itens import NFCeItens


class NFCe(Base):
    __tablename__ = "nfce"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emitente: Mapped[str] = mapped_column(String(255), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    endereco: Mapped[str] = mapped_column(String(500))
    valor_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    serie: Mapped[str] = mapped_column(String(20))
    data_emissao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    protocolo: Mapped[str] = mapped_column(String(50))
    chave_acesso: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    consumidor: Mapped[str] = mapped_column(String(255), nullable=True)
    tributos: Mapped[float] = mapped_column(Numeric(10, 2))

    itens: Mapped[list["NFCeItens"]] = relationship(
        "NFCeItens", back_populates="nota", cascade="all, delete-orphan"
    )
