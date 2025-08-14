from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, TIMESTAMP, Integer, ForeignKey, String
from sqlalchemy.sql import func
from app.core.database import Base

class TransacaoParcela(Base):
    __tablename__ = "transacoes_parcelas"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantidade: Mapped[int | None] = mapped_column(Integer)
    parcela_inicial: Mapped[int | None] = mapped_column(Integer)
    periodicidade: Mapped[str] = mapped_column(String(20), default="mensal")
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    transacao_id: Mapped[int | None] = mapped_column(ForeignKey("transacoes.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    transacao: Mapped["Transacao"] = relationship(back_populates="parcelas") # type: ignore[name-defined]  # noqa: F821
    usuario: Mapped["Usuario"] = relationship(back_populates="transacoes_parcelas") # type: ignore[name-defined]  # noqa: F821
