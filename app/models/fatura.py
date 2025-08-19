from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from mixins.mixins import Mixins
from mixins.sync_mixins import SyncMixin
from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from models.cartao import Cartao
    from models.transacao import Transacao
    from models.transacao_parcela import TransacaoParcela
    from models.usuario import Usuario


class Fatura(Base, Mixins, SyncMixin):
    __tablename__ = "faturas"

    cartao_id: Mapped[int] = mapped_column(ForeignKey("cartoes.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    # Datas do ciclo
    data_fechamento: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_inicio_periodo: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim_periodo: Mapped[date] = mapped_column(Date, nullable=False)

    # Valores
    valor_total: Mapped[int] = mapped_column(Integer, default=0)
    valor_pago: Mapped[int] = mapped_column(Integer, default=0)
    valor_minimo: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    paga: Mapped[bool] = mapped_column(Boolean, default=False)
    vencida: Mapped[bool] = mapped_column(Boolean, default=False)

    # Informações adicionais
    juros_mora: Mapped[int | None] = mapped_column(Integer, default=0)
    multa: Mapped[int | None] = mapped_column(Integer, default=0)
    observacoes: Mapped[str | None] = mapped_column(Text)

    # Relacionamentos
    cartao: Mapped["Cartao"] = relationship(back_populates="faturas")
    usuario: Mapped["Usuario"] = relationship(back_populates="faturas")
    transacoes: Mapped[list["Transacao"]] = relationship(back_populates="fatura")
    pagamentos: Mapped[list["FaturaPagamento"]] = relationship(
        back_populates="fatura", cascade="all, delete-orphan"
    )
    parcelas: Mapped[list["TransacaoParcela"]] = relationship(back_populates="fatura")

    @property
    def saldo_devedor(self) -> int:
        """Retorna o saldo ainda em aberto da fatura"""
        return self.valor_total - self.valor_pago

    @property
    def percentual_pago(self) -> float:
        """Retorna o percentual pago da fatura"""
        if self.valor_total == 0:
            return 100.0
        return float((self.valor_pago / self.valor_total) * 100)

    @property
    def dias_vencimento(self) -> int:
        """Retorna quantos dias faltam para o vencimento (negativo se vencida)"""
        return (self.data_vencimento - date.today()).days

    @classmethod
    def gerar_proxima_fatura(cls, cartao: "Cartao") -> "Fatura":
        """Gera a próxima fatura baseada no ciclo do cartão"""
        hoje = date.today()

        # Calcula as datas baseado no ciclo do cartão
        if hoje.day <= cartao.dia_fechamento:
            # Ainda estamos no período atual
            data_fechamento = date(hoje.year, hoje.month, cartao.dia_fechamento)
        else:
            # Já passou do fechamento, próximo mês
            if hoje.month == 12:
                data_fechamento = date(hoje.year + 1, 1, cartao.dia_fechamento)
            else:
                data_fechamento = date(hoje.year, hoje.month + 1, cartao.dia_fechamento)

        # Calcula data de vencimento
        data_vencimento = data_fechamento + timedelta(days=cartao.dias_vencimento)

        # Período da fatura (mês anterior ao fechamento)
        if data_fechamento.month == 1:
            data_inicio = date(data_fechamento.year - 1, 12, cartao.dia_fechamento + 1)
        else:
            data_inicio = date(
                data_fechamento.year,
                data_fechamento.month - 1,
                cartao.dia_fechamento + 1,
            )

        data_fim = data_fechamento

        return cls(
            cartao_id=cartao.id,
            usuario_id=cartao.usuario_id,
            data_fechamento=data_fechamento,
            data_vencimento=data_vencimento,
            data_inicio_periodo=data_inicio,
            data_fim_periodo=data_fim,
            valor_total=0,
            valor_pago=0,
            valor_minimo=0,
        )

    def calcular_valor_minimo(self) -> int:
        """Calcula o valor mínimo da fatura (geralmente 15% do total)"""
        percentual_minimo = Decimal("0.15")  # 15%
        valor_minimo = (Decimal(self.valor_total) * percentual_minimo).quantize(
            Decimal("1")
        )
        # Valor mínimo nunca pode ser menor que R$ 50,00 (5000 centavos)
        return max(int(valor_minimo), 5000)

    def adicionar_transacao(self, transacao: "Transacao") -> None:
        """Adiciona uma transação à fatura e recalcula o total"""
        self.valor_total += transacao.valor
        self.valor_minimo = self.calcular_valor_minimo()

    def marcar_como_vencida(self) -> None:
        """Marca a fatura como vencida e calcula juros/multa"""
        if not self.vencida and date.today() > self.data_vencimento:
            self.vencida = True
            # Multa de 2% sobre o saldo devedor
            self.multa = int(Decimal(self.saldo_devedor) * Decimal("0.02"))
            # Juros de 1% ao mês (exemplo)
            self.juros_mora = int(Decimal(self.saldo_devedor) * Decimal("0.01"))


class FaturaPagamento(Base, Mixins, SyncMixin):
    __tablename__ = "faturas_pagamentos"

    fatura_id: Mapped[int] = mapped_column(ForeignKey("faturas.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    valor_pago: Mapped[int] = mapped_column(Integer, nullable=False)
    data_pagamento: Mapped[date] = mapped_column(Date, nullable=False)
    forma_pagamento: Mapped[str] = mapped_column(String(50))  # PIX, TED, Boleto, etc.
    comprovante: Mapped[str | None] = mapped_column(String(255))  # Path do arquivo
    observacoes: Mapped[str | None] = mapped_column(Text)

    # Relacionamentos
    fatura: Mapped[Fatura] = relationship(back_populates="pagamentos")
    parcelas: Mapped[list["TransacaoParcela"]] = relationship(
        back_populates="fatura_pagamento", cascade="all, delete-orphan"
    )
    usuario: Mapped["Usuario"] = relationship(back_populates="pagamentos_faturas")  # type: ignore[name-defined]
