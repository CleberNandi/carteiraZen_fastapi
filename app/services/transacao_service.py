from datetime import date

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cartao import Cartao
from app.models.conta import Conta
from app.models.fatura import Fatura
from app.models.transacao import Transacao
from app.schemas.transacao import TransacaoRead


class TransacaoService:
    """Serviço com regras de negócio para transações"""

    # ========================================================================
    # MÉTODOS PÚBLICOS - OPERAÇÕES PRINCIPAIS
    # ========================================================================

    @staticmethod
    async def criar_despesa_cartao(
        db: AsyncSession,
        valor_cents: int,
        cartao_id: int,
        categoria_id: int,
        descricao: str,
        usuario_id: int,
        data_transacao: date | None = None,
        parcelas: int = 1,
    ) -> TransacaoRead:
        """Cria despesa no cartão de crédito"""

        if data_transacao is None:
            data_transacao = date.today()

        # Validações
        if valor_cents <= 0:
            raise HTTPException(status_code=400, detail="Valor deve ser positivo")

        # Essa validação é relativa. Caso eu queira lançar o financiamento da minha casa, 360 meses?
        if parcelas < 1 or parcelas > 48:
            raise HTTPException(
                status_code=400, detail="Parcelas devem ser entre 1 e 48"
            )

        # Busca e valida cartão
        cartao = await TransacaoService._validar_cartao(db, cartao_id, usuario_id)

        # Valida limite disponível
        limite_disponivel = await TransacaoService._calcular_limite_disponivel(
            db, cartao
        )
        if valor_cents > limite_disponivel:
            raise HTTPException(
                status_code=400,
                detail=f"Limite insuficiente. Disponível: R$ {limite_disponivel / 100:.2f}",
            )

        # Busca ou cria fatura atual
        fatura = await TransacaoService._obter_fatura_atual(db, cartao, data_transacao)

        # Valor por parcela
        valor_parcela = valor_cents // parcelas
        valor_ultima_parcela = valor_cents - (valor_parcela * (parcelas - 1))

        # Cria transação principal (apenas para controle)
        transacao_principal = Transacao(
            tipo="DESPESA",
            valor_cents=valor_cents,
            # TODO(Cleber): Verificar data_transacao.  # noqa: FIX002
            # 001
            data_vencimento=data_transacao,
            data_lancamento=data_transacao,
            data_efetivacao=data_transacao,
            descricao=f"{descricao}" + (f" ({parcelas}x)" if parcelas > 1 else ""),
            efetivada=True,
            cor="#FF6B6B",
            conta_origem_id=cartao.conta_id,
            categoria_id=categoria_id,
            fatura_id=fatura.id,
            usuario_id=usuario_id,
        )

        db.add(transacao_principal)
        await db.flush()  # Para obter o ID

        # Se parcelado, cria parcelas
        if parcelas > 1:
            await TransacaoService._criar_parcelas(
                db,
                transacao_principal.id,
                valor_parcela,
                valor_ultima_parcela,
                parcelas,
                data_transacao,
                fatura.id,
                usuario_id,
            )

        # Atualiza valor da fatura
        await TransacaoService._atualizar_fatura(db, fatura, valor_cents)

        await db.commit()
        await db.refresh(transacao_principal)

        return TransacaoRead.model_validate(transacao_principal)

    @staticmethod
    async def criar_receita(
        db: AsyncSession,
        valor_cents: int,
        conta_id: int,
        categoria_id: int,
        descricao: str,
        usuario_id: int,
        data_transacao: date | None = None,
    ) -> TransacaoRead:
        """Cria receita e credita na conta"""

        if data_transacao is None:
            data_transacao = date.today()

        # Validações
        if valor_cents <= 0:
            raise HTTPException(status_code=400, detail="Valor deve ser positivo")

        # Busca e valida conta
        conta = await TransacaoService._validar_conta(db, conta_id, usuario_id)

        # Cria transação
        transacao = Transacao(
            tipo="RECEITA",
            valor_cents=valor_cents,
            # TODO(Cleber): Verificar data_transacao.  # noqa: FIX002
            # 001
            data_vencimento=data_transacao,
            data_lancamento=data_transacao,
            data_efetivacao=data_transacao,
            descricao=descricao,
            efetivada=True,
            cor="#4ECDC4",
            conta_destino_id=conta_id,
            categoria_id=categoria_id,
            usuario_id=usuario_id,
        )

        db.add(transacao)

        # Atualiza saldo da conta
        conta.saldo_cents += valor_cents

        await db.commit()
        await db.refresh(transacao)

        return TransacaoRead.model_validate(transacao)

    @staticmethod
    async def criar_despesa_conta(
        db: AsyncSession,
        valor_cents: int,
        conta_id: int,
        categoria_id: int,
        descricao: str,
        usuario_id: int,
        meio_pagamento: str = "DEBITO",  # DEBITO, PIX, DINHEIRO
        data_transacao: date | None = None,
    ) -> TransacaoRead:
        """Cria despesa diretamente na conta (débito, PIX, dinheiro)"""

        if data_transacao is None:
            data_transacao = date.today()

        # Validações
        if valor_cents <= 0:
            raise HTTPException(status_code=400, detail="Valor deve ser positivo")

        # Busca e valida conta
        conta = await TransacaoService._validar_conta(db, conta_id, usuario_id)

        # Valida saldo (permite cheque especial)
        saldo_disponivel = conta.saldo_cents + conta.cheque_especial_cents
        if valor_cents > saldo_disponivel:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Disponível: R$ {saldo_disponivel / 100:.2f}",
            )

        # Cria transação
        transacao = Transacao(
            tipo="DESPESA",
            valor_cents=valor_cents,
            data_vencimento=data_transacao,
            data_lancamento=data_transacao,
            data_efetivacao=data_transacao,
            descricao=f"{descricao} ({meio_pagamento})",
            efetivada=True,
            cor="#FF6B6B",
            conta_origem_id=conta_id,
            categoria_id=categoria_id,
            usuario_id=usuario_id,
        )

        db.add(transacao)

        # Debita da conta
        conta.saldo_cents -= valor_cents

        await db.commit()
        await db.refresh(transacao)

        return TransacaoRead.model_validate(transacao)

    @staticmethod
    async def transferir_entre_contas(
        db: AsyncSession,
        valor_cents: int,
        conta_origem_id: int,
        conta_destino_id: int,
        descricao: str,
        usuario_id: int,
        data_transacao: date | None = None,
    ) -> dict[str, TransacaoRead]:
        """Transfere dinheiro entre contas do mesmo usuário"""

        if data_transacao is None:
            data_transacao = date.today()

        # Validações
        if valor_cents <= 0:
            raise HTTPException(status_code=400, detail="Valor deve ser positivo")

        if conta_origem_id == conta_destino_id:
            raise HTTPException(status_code=400, detail="Contas devem ser diferentes")

        # Busca e valida contas
        conta_origem = await TransacaoService._validar_conta(
            db, conta_origem_id, usuario_id
        )
        conta_destino = await TransacaoService._validar_conta(
            db, conta_destino_id, usuario_id
        )

        # Valida saldo origem
        saldo_disponivel = conta_origem.saldo_cents + conta_origem.cheque_especial_cents
        if valor_cents > saldo_disponivel:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente na conta origem. Disponível: R$ {saldo_disponivel / 100:.2f}",
            )

        # Cria transação de débito (origem)
        transacao_debito = Transacao(
            tipo="TRANSFERENCIA",
            valor_cents=valor_cents,
            data_vencimento=data_transacao,
            data_lancamento=data_transacao,
            data_efetivacao=data_transacao,
            descricao=f"Transferência para {conta_destino.nome} - {descricao}",
            efetivada=True,
            cor="#FFB74D",
            conta_origem_id=conta_origem_id,
            conta_destino_id=conta_destino_id,
            usuario_id=usuario_id,
        )

        # Cria transação de crédito (destino)
        transacao_credito = Transacao(
            tipo="TRANSFERENCIA",
            valor_cents=valor_cents,
            data_vencimento=data_transacao,
            data_lancamento=data_transacao,
            data_efetivacao=data_transacao,
            descricao=f"Transferência de {conta_origem.nome} - {descricao}",
            efetivada=True,
            cor="#4ECDC4",
            conta_origem_id=conta_origem_id,
            conta_destino_id=conta_destino_id,
            transacao_pai_id=None,  # Será atualizado após salvar a primeira
            usuario_id=usuario_id,
        )

        db.add(transacao_debito)
        await db.flush()

        # Vincula as transações
        transacao_credito.transacao_pai_id = transacao_debito.id
        db.add(transacao_credito)

        # Atualiza saldos
        conta_origem.saldo_cents -= valor_cents
        conta_destino.saldo_cents += valor_cents

        await db.commit()
        await db.refresh(transacao_debito)
        await db.refresh(transacao_credito)

        return {
            "debito": TransacaoRead.model_validate(transacao_debito),
            "credito": TransacaoRead.model_validate(transacao_credito),
        }

    # ========================================================================
    # MÉTODOS PRIVADOS - HELPERS
    # ========================================================================

    @staticmethod
    async def _validar_cartao(
        db: AsyncSession, cartao_id: int, usuario_id: int
    ) -> Cartao:
        """Valida se cartão existe e pertence ao usuário"""
        result = await db.execute(
            select(Cartao).where(
                and_(
                    Cartao.id == cartao_id,
                    Cartao.usuario_id == usuario_id,
                    Cartao.ativo.is_(True),
                )
            )
        )
        cartao = result.scalar_one_or_none()
        if not cartao:
            raise HTTPException(
                status_code=404, detail="Cartão não encontrado ou inativo"
            )
        return cartao

    @staticmethod
    async def _validar_conta(db: AsyncSession, conta_id: int, usuario_id: int) -> Conta:
        """Valida se conta existe e pertence ao usuário"""
        result = await db.execute(
            select(Conta).where(
                and_(
                    Conta.id == conta_id,
                    Conta.usuario_id == usuario_id,
                    Conta.ativo.is_(True),
                )
            )
        )
        conta = result.scalar_one_or_none()
        if not conta:
            raise HTTPException(
                status_code=404, detail="Conta não encontrada ou inativa"
            )
        return conta

    @staticmethod
    async def _calcular_limite_disponivel(db: AsyncSession, cartao: Cartao) -> int:
        """Calcula limite disponível do cartão"""
        # Soma todas as faturas em aberto
        result = await db.execute(
            select(Fatura).where(
                and_(
                    Fatura.conta_cartao_id == cartao.id,
                    Fatura.pago.is_(False),
                    Fatura.ativo.is_(True),
                )
            )
        )
        faturas_abertas = result.scalars().all()

        valor_utilizado = sum(fatura.valor_cents for fatura in faturas_abertas)
        limite_disponivel = cartao.limite_cents - valor_utilizado

        return max(0, limite_disponivel)

    @staticmethod
    async def _obter_fatura_atual(
        db: AsyncSession, cartao: Cartao, data_transacao: date
    ) -> Fatura:
        """Busca fatura atual ou cria nova"""

        # TODO (Cleber): Implementar lógica de ciclo da fatura baseado em fechamento/vencimento  # noqa: FIX002
        # 002
        # Por enquanto, busca fatura não paga mais recente
        result = await db.execute(
            select(Fatura)
            .where(
                and_(
                    Fatura.conta_cartao_id == cartao.id,
                    Fatura.pago.is_(False),
                    Fatura.ativo.is_(True),
                )
            )
            .order_by(Fatura.vencimento.desc())
            .limit(1)
        )
        fatura = result.scalar_one_or_none()

        # Se não existe fatura em aberto, cria nova
        if not fatura:
            fatura = Fatura(
                valor_cents=0,
                pago=False,
                cor=cartao.cor,
                fechamento=cartao.fechamento,
                vencimento=cartao.vencimento,
                conta_cartao_id=cartao.id,
                usuario_id=cartao.usuario_id,
            )
            db.add(fatura)
            await db.flush()

        return fatura

    @staticmethod
    async def _atualizar_fatura(
        db: AsyncSession, fatura: Fatura, valor_cents: int
    ) -> None:
        """Atualiza valor da fatura"""
        fatura.valor_cents += valor_cents

    @staticmethod
    async def _criar_parcelas(
        db: AsyncSession,
        transacao_pai_id: int,
        valor_parcela: int,
        valor_ultima_parcela: int,
        total_parcelas: int,
        data_base: date,
        fatura_id: int,
        usuario_id: int,
    ) -> None:
        """Cria parcelas para transação parcelada"""
        # Implementação simplificada - assumindo que todas ficam na mesma fatura
        # Em um sistema real, parcelas futuras iriam para faturas futuras

        from app.models.transacao_parcela import TransacaoParcela

        for i in range(total_parcelas):
            valor = valor_ultima_parcela if i == total_parcelas - 1 else valor_parcela

            parcela = TransacaoParcela(
                numero_parcela=i + 1,
                total_parcelas=total_parcelas,
                valor_cents=valor,
                data_vencimento=data_base,  # TODO (Cleber): Calcular data correta da parcela  # noqa: FIX002, TD003
                transacao_id=transacao_pai_id,
                fatura_id=fatura_id,
                usuario_id=usuario_id,
            )
            db.add(parcela)
