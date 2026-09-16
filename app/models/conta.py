from mixins.sync_mixins import SyncMixin
from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.mixins.mixins import Mixins


class Conta(Base, Mixins, SyncMixin):
    __tablename__ = "contas"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    saldo_cents: Mapped[int] = mapped_column(BigInteger, default=0)
    cheque_especial_cents: Mapped[int] = mapped_column(BigInteger, default=0)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    incluir_na_soma_inicial: Mapped[bool] = mapped_column(Boolean, default=True)
    conta_padrao: Mapped[bool] = mapped_column(Boolean, default=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    banco_id: Mapped[int | None] = mapped_column(ForeignKey("bancos.id"), nullable=True)

    # Relacionamentos
    usuario: Mapped["Usuario"] = relationship(back_populates="contas")  # type: ignore[name-defined]  # noqa: F821
    banco: Mapped["Banco"] = relationship(back_populates="contas")  # type: ignore[name-defined]  # noqa: F821
    cartoes: Mapped[list["Cartao"]] = relationship(back_populates="conta")  # type: ignore[name-defined]  # noqa: F821
