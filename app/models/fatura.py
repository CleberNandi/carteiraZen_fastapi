from mixins.mixins import Mixins
from mixins.sync_mixins import SyncMixin
from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Fatura(Base, Mixins, SyncMixin):
    __tablename__ = "faturas"

    valor_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    pago: Mapped[bool] = mapped_column(Boolean, default=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    fechamento: Mapped[Date] = mapped_column(Date, nullable=False)
    vencimento: Mapped[Date] = mapped_column(Date, nullable=False)
    conta_cartao_id: Mapped[int] = mapped_column(
        ForeignKey("cartoes.id"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    # Relacionamentos
    cartao: Mapped["Cartao"] = relationship(  # noqa: F821 # type: ignore
        "Cartao", back_populates="faturas"
    )
    usuario: Mapped["Usuario"] = relationship(  # noqa: F821 # type: ignore
        "Usuario", back_populates="faturas"
    )
    transacoes: Mapped["Transacao"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Transacao", back_populates="fatura", cascade="all, delete-orphan"
    )
