from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    valor_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    data_vencimento: Mapped[Date] = mapped_column(Date, nullable=False)
    data_lancamento: Mapped[Date] = mapped_column(Date, nullable=False)
    data_efetivacao: Mapped[Date] = mapped_column(Date, nullable=False)
    encargos_cents: Mapped[int | None] = mapped_column(BigInteger)
    descontos_cents: Mapped[int | None] = mapped_column(BigInteger)
    recorrente: Mapped[bool] = mapped_column(Boolean, default=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    efetivada: Mapped[bool] = mapped_column(Boolean, default=True)
    cor: Mapped[str] = mapped_column(String(7), nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[TIMESTAMP | None] = mapped_column(TIMESTAMP)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    transacao_pai_id: Mapped[int | None] = mapped_column(ForeignKey("transacoes.id"))
    conta_origem_id: Mapped[int | None] = mapped_column(ForeignKey("contas.id"))
    conta_destino_id: Mapped[int | None] = mapped_column(ForeignKey("contas.id"))
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"))
    sub_categoria_id: Mapped[int | None] = mapped_column(
        ForeignKey("sub_categorias.id")
    )
    fatura_id: Mapped[int | None] = mapped_column(ForeignKey("faturas.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    conta_origem: Mapped["Conta"] = relationship(foreign_keys=[conta_origem_id])  # type: ignore[name-defined]  # noqa: F821
    conta_destino: Mapped["Conta"] = relationship(foreign_keys=[conta_destino_id])  # type: ignore[name-defined]  # noqa: F821

    usuario: Mapped["Usuario"] = relationship(back_populates="transacoes")  # type: ignore[name-defined]  # noqa: F821
    categoria: Mapped["Categoria"] = relationship(back_populates="transacoes")  # type: ignore[name-defined]  # noqa: F821
    sub_categoria: Mapped["SubCategoria"] = relationship(back_populates="transacoes")  # type: ignore[name-defined]  # noqa: F821
    fatura: Mapped["Fatura"] = relationship(back_populates="transacoes")  # type: ignore[name-defined]  # noqa: F821
    parcelas: Mapped[list["TransacaoParcela"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="transacao", cascade="all, delete-orphan"
    )
