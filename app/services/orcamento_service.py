from typing import TYPE_CHECKING

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.transacao import Transacao

if TYPE_CHECKING:
    from app.models.orcamento import Orcamento


class OrcamentoService:
    @staticmethod
    def criar_orcamento(
        db: Session,
        usuario_id: int,
        categoria_id: int,
        ano: int,
        mes: int,
        valor_limite: int,
        notificar_em: int = 80,
    ) -> "Orcamento":
        """Cria um novo orçamento"""
        from models.orcamento import Orcamento

        # Verifica se já existe orçamento para esta categoria no período
        orcamento_existente = (
            db.query(Orcamento)
            .filter(
                and_(
                    Orcamento.usuario_id == usuario_id,
                    Orcamento.categoria_id == categoria_id,
                    Orcamento.ano == ano,
                    Orcamento.mes == mes,
                )
            )
            .first()
        )

        if orcamento_existente:
            message = "Já existe orçamento para esta categoria no período"
            raise ValueError(message)

        orcamento = Orcamento(
            usuario_id=usuario_id,
            categoria_id=categoria_id,
            ano=ano,
            mes=mes,
            valor_limite=valor_limite,
            valor_disponivel=valor_limite,
            notificar_em=notificar_em,
        )

        db.add(orcamento)
        db.commit()
        db.refresh(orcamento)

        return orcamento

    @staticmethod
    def atualizar_orcamento_por_transacao(
        db: Session, transacao: Transacao, operacao: str = "adicionar"
    ) -> None:
        """Atualiza orçamentos baseado em uma transação"""
        from models.orcamento import Orcamento

        # Busca orçamento da categoria no período da transação
        orcamento = (
            db.query(Orcamento)
            .filter(
                and_(
                    Orcamento.usuario_id == transacao.usuario_id,
                    Orcamento.categoria_id == transacao.categoria_id,
                    Orcamento.ano == transacao.data_transacao.year,
                    Orcamento.mes == transacao.data_transacao.month,
                    Orcamento.ativo.is_(True),
                )
            )
            .first()
        )

        if orcamento:
            orcamento.atualizar_valor_gasto(transacao.valor, operacao)
            db.commit()

    @staticmethod
    def obter_orcamentos_excedidos(db: Session, usuario_id: int) -> list["Orcamento"]:
        """Obtém orçamentos que excederam o limite"""
        from models.orcamento import Orcamento

        return (
            db.query(Orcamento)
            .filter(
                and_(
                    Orcamento.usuario_id == usuario_id,
                    Orcamento.valor_gasto > Orcamento.valor_limite,
                    Orcamento.ativo.is_(True),
                )
            )
            .all()
        )

    @staticmethod
    def obter_orcamentos_para_notificar(
        db: Session, usuario_id: int
    ) -> list["Orcamento"]:
        """Obtém orçamentos que devem gerar notificação"""
        from models.orcamento import Orcamento

        orcamentos = (
            db.query(Orcamento)
            .filter(and_(Orcamento.usuario_id == usuario_id, Orcamento.ativo.is_(True)))
            .all()
        )

        return [o for o in orcamentos if o.deve_notificar and not o.excedeu_limite]

    @staticmethod
    def obter_resumo_orcamentos(
        db: Session, usuario_id: int, ano: int, mes: int
    ) -> dict[str, str | int | float]:
        """Obtém resumo dos orçamentos do período"""
        from models.orcamento import Orcamento

        orcamentos = (
            db.query(Orcamento)
            .filter(
                and_(
                    Orcamento.usuario_id == usuario_id,
                    Orcamento.ano == ano,
                    Orcamento.mes == mes,
                    Orcamento.ativo.is_(True),
                )
            )
            .all()
        )

        total_orcado = sum(o.valor_limite for o in orcamentos)
        total_gasto = sum(o.valor_gasto for o in orcamentos)
        total_disponivel = sum(o.valor_disponivel for o in orcamentos)

        orcamentos_excedidos = len([o for o in orcamentos if o.excedeu_limite])
        orcamentos_alerta = len(
            [o for o in orcamentos if o.deve_notificar and not o.excedeu_limite]
        )

        return {
            "total_orcamentos": len(orcamentos),
            "total_orcado": total_orcado,
            "total_gasto": total_gasto,
            "total_disponivel": total_disponivel,
            "percentual_usado": float(total_gasto / total_orcado * 100)
            if total_orcado > 0
            else 0.0,
            "orcamentos_excedidos": orcamentos_excedidos,
            "orcamentos_alerta": orcamentos_alerta,
            "orcamentos_ok": len(orcamentos) - orcamentos_excedidos - orcamentos_alerta,
        }
