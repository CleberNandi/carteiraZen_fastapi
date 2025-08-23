from mixins.sync_mixins import SyncMixin
from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.mixins.mixins import Mixins


class Cartao(Base, Mixins, SyncMixin):
    __tablename__ = "cartoes"

    numero: Mapped[str] = mapped_column(String(16), nullable=False)
    descricao: Mapped[str] = mapped_column(String(20), nullable=False)
    bandeira: Mapped[str] = mapped_column(String(20), nullable=False)
    limite_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    dia_fechamento: Mapped[int] = mapped_column(nullable=False)
    dias_vencimento: Mapped[int] = mapped_column(nullable=False)
    cartao_padrao: Mapped[bool] = mapped_column(Boolean, default=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    conta_id: Mapped[int] = mapped_column(ForeignKey("contas.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    # Relacionamentos
    faturas: Mapped[list["Fatura"]] = relationship(  # noqa: F821 # type: ignore
        "Fatura", back_populates="cartao", cascade="all, delete-orphan"
    )
    usuario: Mapped["Usuario"] = relationship(  # noqa: F821 # type: ignore
        "Usuario", back_populates="cartoes"
    )
    conta: Mapped["Conta"] = relationship(  # noqa: F821 # type: ignore
        "Conta", back_populates="cartoes"
    )
