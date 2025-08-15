from mixins.mixins import Mixins
from mixins.sync_mixins import SyncMixin
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TransacaoParcela(Base, Mixins, SyncMixin):
    __tablename__ = "transacoes_parcelas"

    quantidade: Mapped[int | None] = mapped_column(Integer)
    parcela_inicial: Mapped[int | None] = mapped_column(Integer)
    periodicidade: Mapped[str] = mapped_column(String(20), default="mensal")
    transacao_id: Mapped[int | None] = mapped_column(ForeignKey("transacoes.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    transacao: Mapped["Transacao"] = relationship(back_populates="parcelas")  # type: ignore[name-defined]  # noqa: F821
    usuario: Mapped["Usuario"] = relationship(back_populates="transacoes_parcelas")  # type: ignore[name-defined]  # noqa: F821
