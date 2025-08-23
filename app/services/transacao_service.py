from datetime import date, timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cartao import Cartao
from app.models.conta import Conta
from app.models.fatura import Fatura
from app.models.transacao import Transacao
from app.models.transacao_parcela import TransacaoParcela
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
        parcela_inicial: int = 1,
    ) -> TransacaoRead:
        """Cria despesa no cartão de crédito"""

        if data_transacao is None:
            data_transacao = date.today()

        # Validações
        if valor_cents <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor deve ser positivo",
            )

        # Essa validação é relativa. Caso eu queira lançar o financiamento da minha casa, 360 meses?
        if parcelas < 1 or parcelas > 48:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parcelas devem ser entre 1 e 48",
            )

        if parcela_inicial < 1 or parcela_inicial > parcelas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parcela inicial inválida",
            )

        # Busca e valida cartão
        cartao = await TransacaoService._validar_cartao(db, cartao_id, usuario_id)

        # Valida limite disponível
        limite_disponivel = await TransacaoService._calcular_limite_disponivel(
            db, cartao
        )
        if valor_cents > limite_disponivel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limite insuficiente. Disponível: R$ {limite_disponivel / 100:.2f}",
            )

        # Cria transação principal (apenas para controle)
        transacao_principal = Transacao(
            tipo="DESPESA",
            valor_cents=valor_cents,
            data_vencimento=data_transacao,
            data_lancamento=data_transacao,
            data_efetivacao=data_transacao,
            descricao=f"{descricao}" + (f" ({parcelas}x)" if parcelas > 1 else ""),
            efetivada=True,
            cor="#FF6B6B",
            conta_origem_id=cartao.conta_id,
            categoria_id=categoria_id,
            usuario_id=usuario_id,
        )

        db.add(transacao_principal)
        await db.flush()  # Para obter o ID

        parcelas_criadas = await TransacaoService._criar_parcelas(
            db=db,
            transacao_id=transacao_principal.id,
            valor_total_cents=valor_cents,
            total_parcelas=parcelas,
            parcela_inicial=parcela_inicial,
            data_base=data_transacao,
            cartao=cartao,
            usuario_id=usuario_id,
        )

        await db.commit()
        await db.refresh(transacao_principal)

        return {
            "transacao": {
                "id": transacao_principal.id,
                "tipo": transacao_principal.tipo,
                "valor_cents": transacao_principal.valor_cents,
                "data_vencimento": transacao_principal.data_vencimento,
                "data_lancamento": transacao_principal.data_lancamento,
                "data_efetivacao": transacao_principal.data_efetivacao,
                "encargos_cents": transacao_principal.encargos_cents,
                "descontos_cents": transacao_principal.descontos_cents,
                "recorrente": transacao_principal.recorrente,
                "descricao": transacao_principal.descricao,
                "efetivada": transacao_principal.efetivada,
                "cor": transacao_principal.cor,
                "transacao_pai_id": transacao_principal.transacao_pai_id,
                "conta_origem_id": transacao_principal.conta_origem_id,
                "conta_destino_id": transacao_principal.conta_destino_id,
                "categoria_id": transacao_principal.categoria_id,
                "sub_categoria_id": transacao_principal.sub_categoria_id,
                "fatura_id": transacao_principal.fatura_id,
                "usuario_id": transacao_principal.usuario_id,
                "created_at": transacao_principal.created_at,
                "updated_at": transacao_principal.updated_at,
                "deleted_at": transacao_principal.deleted_at,
                "ativo": transacao_principal.ativo,
            },
            "parcelas": [
                {
                    "numero": p.numero_parcela,
                    "valor": float(p.valor_decimal),
                    "vencimento": p.data_vencimento,
                    "fatura_id": p.fatura_id,
                }
                for p in parcelas_criadas
            ],
            "resumo": {
                "valor_total": float(Decimal(valor_cents) / 100),
                "total_parcelas": parcelas,
                "parcela_inicial": parcela_inicial,
                "parcelas_criadas": len(parcelas_criadas),
            },
        }

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

    @staticmethod
    async def cancelar_transacao_parcelada(
        db: AsyncSession,
        transacao_id: int,
        usuario_id: int,
        *,
        cancelar_parcelas_pagas: bool = False,
    ) -> dict:
        """Cancela transação parcelada e suas parcelas"""

        # Busca transação principal
        result = await db.execute(
            select(Transacao).where(
                and_(Transacao.id == transacao_id, Transacao.usuario_id == usuario_id)
            )
        )
        transacao = result.scalar_one_or_none()

        if not transacao:
            raise HTTPException(status_code=404, detail="Transação não encontrada")

        # Busca todas as parcelas
        result = await db.execute(
            select(TransacaoParcela).where(
                TransacaoParcela.transacao_id == transacao_id
            )
        )
        parcelas = result.scalars().all()

        parcelas_canceladas = 0
        valor_cancelado = 0
        faturas_afetadas = set()

        for parcela in parcelas:
            # Se parcela já está paga e não deve cancelar pagas, pula
            if parcela.paga and not cancelar_parcelas_pagas:
                continue

            # Cancela a parcela
            parcela.cancelada = True
            parcelas_canceladas += 1
            valor_cancelado += parcela.valor_cents

            # Remove valor da fatura se não estava paga
            if not parcela.paga and parcela.fatura_id:
                result = await db.execute(
                    select(Fatura).where(Fatura.id == parcela.fatura_id)
                )
                fatura = result.scalar_one_or_none()
                if fatura:
                    fatura.valor_total -= Decimal(parcela.valor_cents) / 100
                    fatura.valor_minimo = fatura.calcular_valor_minimo()
                    faturas_afetadas.add(fatura.id)

        # Marca transação principal como cancelada se todas parcelas foram canceladas
        if parcelas_canceladas == len(parcelas):
            transacao.efetivada = False
            transacao.descricao += " [CANCELADA]"

        await db.commit()

        return {
            "message": "Transação cancelada com sucesso",
            "parcelas_canceladas": parcelas_canceladas,
            "valor_cancelado": float(Decimal(valor_cancelado) / 100),
            "faturas_afetadas": list(faturas_afetadas),
        }

    @staticmethod
    async def listar_parcelas_transacao(
        db: AsyncSession, transacao_id: int, usuario_id: int
    ) -> list[dict]:
        """Lista todas as parcelas de uma transação"""

        result = await db.execute(
            select(TransacaoParcela)
            .where(
                and_(
                    TransacaoParcela.transacao_id == transacao_id,
                    TransacaoParcela.usuario_id == usuario_id,
                )
            )
            .order_by(TransacaoParcela.numero_parcela)
        )
        parcelas = result.scalars().all()

        return [
            {
                "id": p.id,
                "numero_parcela": p.numero_parcela,
                "total_parcelas": p.total_parcelas,
                "valor": float(p.valor_decimal),
                "data_vencimento": p.data_vencimento,
                "paga": p.paga,
                "cancelada": p.cancelada,
                "fatura_id": p.fatura_id,
                "status": "Cancelada"
                if p.cancelada
                else "Paga"
                if p.paga
                else "Pendente",
            }
            for p in parcelas
        ]

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
                    Fatura.cartao_id == cartao.id,
                    Fatura.paga.is_(False),
                    Fatura.ativo.is_(True),
                )
            )
        )
        faturas_abertas = result.scalars().all()

        valor_utilizado = sum(fatura.valor_total for fatura in faturas_abertas)
        limite_disponivel = cartao.limite_cents - valor_utilizado

        return max(0, limite_disponivel)

    @staticmethod
    async def _obter_fatura_atual(
        db: AsyncSession, cartao: Cartao, data_parcela: date
    ) -> Fatura:
        """Obtém ou cria a fatura correta para a data da parcela"""

        # Calcula as datas de fechamento e vencimento baseado na data da parcela
        # Se a parcela é dia 15 e o cartão fecha dia 10, ela vai para fatura do mês seguinte

        if data_parcela.day <= cartao.dia_fechamento:
            # Parcela vai para fatura do próprio mês
            data_fechamento = data_parcela.replace(day=cartao.dia_fechamento)
        else:
            # Parcela vai para fatura do próximo mês
            data_fechamento = (data_parcela + relativedelta(months=1)).replace(
                day=cartao.dia_fechamento
            )

        data_vencimento = data_fechamento + timedelta(days=cartao.dias_vencimento)

        # Busca fatura existente para este período
        result = await db.execute(
            select(Fatura).where(
                and_(
                    Fatura.cartao_id == cartao.id,
                    Fatura.data_fechamento == data_fechamento,
                    Fatura.ativo.is_(True),
                )
            )
        )
        fatura = result.scalar_one_or_none()

        # Se não existe, cria nova fatura
        if not fatura:
            # Calcula período da fatura
            data_inicio = (data_fechamento - relativedelta(months=1)) + timedelta(
                days=1
            )
            data_fim = data_fechamento

            fatura = Fatura(
                cartao_id=cartao.id,
                usuario_id=cartao.usuario_id,
                data_fechamento=data_fechamento,
                data_vencimento=data_vencimento,
                data_inicio_periodo=data_inicio,
                data_fim_periodo=data_fim,
                valor_total=Decimal("0.00"),
                valor_pago=Decimal("0.00"),
                valor_minimo=Decimal("0.00"),
            )
            db.add(fatura)
            await db.flush()

        return fatura

    @staticmethod
    async def _atualizar_fatura(
        db: AsyncSession, fatura: Fatura, valor_cents: int
    ) -> None:
        """Atualiza valor da fatura"""
        fatura.valor_total += valor_cents

    @staticmethod
    async def _criar_parcelas(
        db: AsyncSession,
        transacao_id: int,
        valor_total_cents: int,
        total_parcelas: int,
        parcela_inicial: int,
        data_base: date,
        cartao: Cartao,
        usuario_id: int,
    ) -> list[TransacaoParcela]:
        """Cria parcelas com distribuição nas faturas"""

        parcelas_para_criar = total_parcelas - parcela_inicial + 1
        valor_parcela = valor_total_cents // parcelas_para_criar
        valor_ultima_parcela = valor_total_cents - (
            valor_parcela * (parcelas_para_criar - 1)
        )

        parcelas_criadas = []

        for i in range(parcelas_para_criar):
            numero_parcela_atual = parcela_inicial + i
            valor_atual = (
                valor_ultima_parcela if i == parcelas_para_criar - 1 else valor_parcela
            )

            # Calcula data de vencimento da parcela (mês + i)
            data_vencimento_parcela = data_base + relativedelta(months=i)

            # Determina em qual fatura esta parcela vai aparecer
            fatura = await TransacaoService._obter_fatura_atual(
                db, cartao, data_vencimento_parcela
            )

            # Cria a parcela
            parcela = TransacaoParcela(
                numero_parcela=numero_parcela_atual,
                total_parcelas=total_parcelas,
                valor_cents=valor_atual,
                data_vencimento=data_vencimento_parcela,
                transacao_id=transacao_id,
                fatura_id=fatura.id,
                usuario_id=usuario_id,
            )

            db.add(parcela)
            parcelas_criadas.append(parcela)

            # Atualiza valor da fatura
            await TransacaoService._atualizar_fatura(db, fatura, valor_atual)

        await db.flush()  # Para obter IDs das parcelas
        return parcelas_criadas
