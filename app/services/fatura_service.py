from datetime import date
from typing import Any

from sqlalchemy import and_, extract
from sqlalchemy.orm import Session

from app.models import cartao, fatura as model_fatura, transacao

Cartao = cartao.Cartao
Fatura = model_fatura.Fatura
FaturaPagamento = model_fatura.FaturaPagamento
Transacao = transacao.Transacao


class FaturaService:
    @staticmethod
    def obter_fatura_atual(db: Session, cartao_id: int) -> Fatura | None:
        """Obtém a fatura atual (em aberto) do cartão"""
        hoje = date.today()
        return (
            db.query(Fatura)
            .filter(
                and_(
                    Fatura.cartao_id == cartao_id,
                    Fatura.data_inicio_periodo <= hoje,
                    Fatura.data_fim_periodo >= hoje,
                    ~Fatura.paga,
                )
            )
            .first()
        )

    @staticmethod
    def obter_proxima_fatura(db: Session, cartao_id: int) -> Fatura | None:
        """Obtém a próxima fatura do cartão"""
        hoje = date.today()
        return (
            db.query(Fatura)
            .filter(
                and_(Fatura.cartao_id == cartao_id, Fatura.data_inicio_periodo > hoje)
            )
            .order_by(Fatura.data_inicio_periodo)
            .first()
        )

    @staticmethod
    def criar_fatura_se_necessario(db: Session, cartao: Cartao) -> Fatura:
        """Cria uma nova fatura se não existir uma atual"""
        fatura_atual = FaturaService.obter_fatura_atual(db, cartao.id)
        if not fatura_atual:
            proxima_fatura = FaturaService.obter_proxima_fatura(db, cartao.id)
            if not proxima_fatura:
                nova_fatura = Fatura.gerar_proxima_fatura(cartao)
                db.add(nova_fatura)
                db.commit()
                db.refresh(nova_fatura)
                return nova_fatura
            return proxima_fatura
        return fatura_atual

    @staticmethod
    def adicionar_transacao_fatura(
        db: Session, transacao: Transacao, cartao: Cartao
    ) -> None:
        """Adiciona uma transação à fatura apropriada"""
        if transacao.data_transacao.day <= cartao.dia_fechamento:
            fatura = FaturaService.obter_fatura_atual(
                db, cartao.id
            ) or FaturaService.criar_fatura_se_necessario(db, cartao)
        else:
            fatura = FaturaService.obter_proxima_fatura(
                db, cartao.id
            ) or FaturaService.criar_fatura_se_necessario(db, cartao)
        transacao.fatura_id = fatura.id
        fatura.adicionar_transacao(transacao)
        db.commit()

    @staticmethod
    def processar_pagamento_fatura(
        db: Session,
        fatura_id: int,
        valor: int,
        forma_pagamento: str,
        usuario_id: int,
        data_pagamento: date | None = None,
    ) -> FaturaPagamento:
        """Processa o pagamento de uma fatura"""
        fatura = db.query(Fatura).filter(Fatura.id == fatura_id).first()
        if not fatura:
            message = "Fatura não encontrada"
            raise ValueError(message)

        if data_pagamento is None:
            data_pagamento = date.today()

        pagamento = FaturaPagamento(
            fatura_id=fatura_id,
            usuario_id=usuario_id,
            valor_pago=valor,
            data_pagamento=data_pagamento,
            forma_pagamento=forma_pagamento,
        )

        fatura.valor_pago += valor
        if fatura.valor_pago >= fatura.valor_total:
            fatura.paga = True
            fatura.valor_pago = fatura.valor_total

        db.add(pagamento)
        db.commit()
        db.refresh(pagamento)
        return pagamento

    @staticmethod
    def obter_faturas_vencidas(db: Session, usuario_id: int) -> list[Fatura]:
        """Obtém todas as faturas vencidas do usuário"""
        hoje = date.today()
        faturas_vencidas = (
            db.query(Fatura)
            .filter(
                and_(
                    Fatura.usuario_id == usuario_id,
                    Fatura.data_vencimento < hoje,
                    ~Fatura.paga,
                )
            )
            .all()
        )
        for fatura in faturas_vencidas:
            fatura.marcar_como_vencida()
        db.commit()
        return faturas_vencidas

    @staticmethod
    def obter_resumo_faturas(
        db: Session, usuario_id: int, ano: int, mes: int
    ) -> dict[str, float]:
        """Obtém resumo das faturas de um período"""
        faturas = (
            db.query(Fatura)
            .filter(
                and_(
                    Fatura.usuario_id == usuario_id,
                    extract("year", Fatura.data_vencimento) == ano,
                    extract("month", Fatura.data_vencimento) == mes,
                )
            )
            .all()
        )
        total_faturas = len(faturas)
        total_valor = sum(f.valor_total for f in faturas)
        total_pago = sum(f.valor_pago for f in faturas)
        faturas_pagas = len([f for f in faturas if f.paga])
        faturas_vencidas = len([f for f in faturas if f.vencida and not f.paga])

        return {
            "total_faturas": total_faturas,
            "faturas_pagas": faturas_pagas,
            "faturas_vencidas": faturas_vencidas,
            "faturas_pendentes": total_faturas - faturas_pagas,
            "valor_total": total_valor,
            "valor_pago": total_pago,
            "saldo_devedor": total_valor - total_pago,
            "percentual_quitado": float(total_pago / total_valor * 100)
            if total_valor > 0
            else 100.0,
        }

    # ===============================
    # NOVOS MÉTODOS CRUD
    # ===============================
    @staticmethod
    def listar_faturas(
        db: Session, usuario_id: int | None = None, cartao_id: int | None = None
    ) -> list[Fatura]:
        """Lista faturas por usuário e/ou cartão"""
        query = db.query(Fatura)
        if usuario_id:
            query = query.filter(Fatura.usuario_id == usuario_id)
        if cartao_id:
            query = query.filter(Fatura.cartao_id == cartao_id)
        return query.all()

    @staticmethod
    def atualizar_fatura(db: Session, fatura_id: int, dados: dict[str, Any]) -> Fatura:
        """Atualiza campos de uma fatura"""
        fatura = db.query(Fatura).filter(Fatura.id == fatura_id).first()
        if not fatura:
            message = "Fatura não encontrada"
            raise ValueError(message)

        # Atualiza apenas campos válidos
        campos_editaveis = {
            "valor_total",
            "valor_pago",
            "paga",
            "data_fechamento",
            "data_vencimento",
            "observacoes",
        }
        for campo, valor in dados.items():
            if campo in campos_editaveis:
                setattr(fatura, campo, valor)

        db.commit()
        db.refresh(fatura)
        return fatura

    @staticmethod
    def deletar_fatura(db: Session, fatura_id: int) -> None:
        """Deleta uma fatura (se permitido)"""
        fatura = db.query(Fatura).filter(Fatura.id == fatura_id).first()
        if not fatura:
            message = "Fatura não encontrada"
            raise ValueError(message)

        # ⚠️ Validação de integridade
        if fatura.transacoes and len(fatura.transacoes) > 0:
            message = "Não é possível deletar fatura com transações associadas"
            raise ValueError(message)

        db.delete(fatura)
        db.commit()
