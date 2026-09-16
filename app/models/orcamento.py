from typing import TYPE_CHECKING

from mixins.sync_mixins import SyncMixin
from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.mixins.mixins import Mixins

if TYPE_CHECKING:
    from models.categoria import Categoria
    from models.usuario import Usuario


class Orcamento(Base, Mixins, SyncMixin):
    __tablename__ = "orcamentos"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id"), nullable=False
    )

    # Período
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Valores em centavos
    valor_limite: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # Ex: 50000 = R$ 500,00
    valor_gasto: Mapped[int] = mapped_column(Integer, default=0)  # Sempre em centavos
    valor_disponivel: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Sempre em centavos

    # Configurações
    notificar_em: Mapped[int] = mapped_column(
        Integer, default=80
    )  # Notificar ao atingir 80%
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relacionamentos
    usuario: Mapped["Usuario"] = relationship(back_populates="orcamentos")
    categoria: Mapped["Categoria"] = relationship(back_populates="orcamentos")

    @property
    def percentual_usado(self) -> float:
        """Retorna o percentual do orçamento já utilizado"""
        if self.valor_limite == 0:
            return 0.0
        return float((self.valor_gasto / self.valor_limite) * 100)

    @property
    def excedeu_limite(self) -> bool:
        """Verifica se o orçamento foi excedido"""
        return self.valor_gasto > self.valor_limite

    @property
    def deve_notificar(self) -> bool:
        """Verifica se deve notificar baseado no percentual configurado"""
        return self.percentual_usado >= self.notificar_em

    def atualizar_valor_gasto(self, valor: int, operacao: str = "adicionar") -> None:
        """
        Atualiza o valor gasto no orçamento
        `valor` deve estar em centavos (int).
        """
        if operacao == "adicionar":
            self.valor_gasto += valor
        elif operacao == "remover":
            self.valor_gasto = max(0, self.valor_gasto - valor)

        self.valor_disponivel = max(0, self.valor_limite - self.valor_gasto)
