# app/services/conta_service.py
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import and_, exists, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conta import Conta
from app.models.transacao import Transacao
from app.models.usuario import Usuario
from app.schemas.conta import (
    ContaCreate,
    ContaListResponse,
    ContaRead,
    ContaResumo,
    ContaUpdate,
    TipoConta,
)


class ContaService:
    @staticmethod
    async def criar(
        db: AsyncSession, conta_in: ContaCreate, current_user: Usuario
    ) -> ContaRead:
        """Cria uma nova conta para o usuário"""

        # Verifica se já existe uma conta com o mesmo nome para o usuário
        existing = await ContaService._conta_nome_existe(
            db, conta_in.nome, current_user.id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma conta com este nome",
            )

        # Se esta conta está sendo marcada como padrão, remove padrão das outras
        if conta_in.conta_padrao:
            await ContaService._remover_conta_padrao(db, current_user.id)

        # Cria a conta
        conta_data = conta_in.model_dump(exclude={"usuario_id"})
        conta = Conta(**conta_data, usuario_id=current_user.id)

        db.add(conta)
        await db.commit()
        await db.refresh(conta)

        return ContaRead.model_validate(conta)

    @staticmethod
    async def buscar_por_id(
        db: AsyncSession, conta_id: int, current_user: Usuario
    ) -> ContaRead:
        """Busca conta por ID (apenas do usuário atual)"""
        conta = await ContaService._validar_conta(db, conta_id, current_user.id)
        return ContaRead.model_validate(conta)

    @staticmethod
    async def listar(
        db: AsyncSession,
        current_user: Usuario,
        skip: int = 0,
        limit: int = 100,
        tipo_filter: str | None = None,
        *,
        incluir_inativas: bool = False,
    ) -> ContaListResponse:
        """Lista contas do usuário com filtros"""

        # Base query
        query = select(Conta).where(Conta.usuario_id == current_user.id)

        # Filtro de ativo
        if not incluir_inativas:
            query = query.where(Conta.ativo.is_(True))

        # Filtro por tipo
        if tipo_filter:
            try:
                tipo_enum = TipoConta(tipo_filter)
                query = query.where(Conta.tipo == tipo_enum)
            except (ValueError, KeyError):
                pass

        # Ordenação
        query = query.order_by(Conta.conta_padrao.desc(), Conta.nome)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Paginação
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        contas = result.scalars().all()

        # Calcula saldo total
        contas_resumo: list[ContaResumo] = []
        saldo_total = 0.0

        for conta in contas:
            tipo_normalizado = conta.tipo.upper()
            print(f"Tipo da conta: {type(conta.tipo)} - Valor: {conta.tipo}")
            resumo = ContaResumo(
                id=conta.id,
                nome=conta.nome,
                tipo=tipo_normalizado,  # type: ignore
                saldo_decimal=float(Decimal(conta.saldo_cents) / 100),
                cor=conta.cor,
                ativo=conta.ativo,
                conta_padrao=conta.conta_padrao,
            )
            contas_resumo.append(resumo)

            if conta.incluir_na_soma_inicial and conta.ativo:
                saldo_total += resumo.saldo_decimal

        return ContaListResponse(
            contas=contas_resumo, total=total, saldo_total=saldo_total
        )

    @staticmethod
    async def atualizar(
        db: AsyncSession, conta_id: int, data: ContaUpdate, current_user: Usuario
    ) -> ContaRead:
        """Atualiza dados da conta"""

        conta = await ContaService._validar_conta(db, conta_id, current_user.id)

        # Verifica duplicata de nome (se nome foi alterado)
        if data.nome and data.nome != conta.nome:
            existing = await ContaService._conta_nome_existe(
                db, data.nome, current_user.id, exclude_id=conta_id
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma conta com este nome",
                )

        # Se está marcando como conta padrão, remove padrão das outras
        if data.conta_padrao is True:
            await ContaService._remover_conta_padrao(
                db, current_user.id, exclude_id=conta_id
            )

        # Atualiza campos
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conta, field, value)

        await db.commit()
        await db.refresh(conta)

        return ContaRead.model_validate(conta)

    @staticmethod
    async def excluir(
        db: AsyncSession, conta_id: int, current_user: Usuario
    ) -> dict[str, bool]:
        """Exclui conta (soft delete) após validações"""

        conta = await ContaService._validar_conta(db, conta_id, current_user.id)

        # Verifica se existem transações vinculadas
        if await ContaService._conta_tem_transacoes(db, conta_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir a conta, existem transações vinculadas",
            )

        # Verifica se não é a única conta ativa
        contas_ativas = await ContaService._contar_contas_ativas(db, current_user.id)
        if contas_ativas <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir a única conta ativa",
            )

        # Se é conta padrão, transfere para outra conta
        if conta.conta_padrao:
            await ContaService._definir_nova_conta_padrao(
                db, current_user.id, exclude_id=conta_id
            )

        # Soft delete
        conta.ativo = False
        await db.commit()

        return {"ok": True}

    @staticmethod
    async def definir_como_padrao(
        db: AsyncSession, conta_id: int, current_user: Usuario
    ) -> ContaRead:
        """Define conta como padrão"""

        conta = await ContaService._validar_conta(db, conta_id, current_user.id)

        if conta.conta_padrao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta conta já é a conta padrão",
            )

        # Remove padrão das outras e define esta como padrão
        await ContaService._remover_conta_padrao(db, current_user.id)
        conta.conta_padrao = True

        await db.commit()
        await db.refresh(conta)

        return ContaRead.model_validate(conta)

    # ========================================================================
    # MÉTODOS PRIVADOS - HELPERS
    # ========================================================================

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
                status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada"
            )
        return conta

    @staticmethod
    async def _conta_nome_existe(
        db: AsyncSession, nome: str, usuario_id: int, exclude_id: int | None = None
    ) -> bool:
        """Verifica se já existe conta com o mesmo nome"""
        query = select(
            exists().where(
                and_(
                    Conta.nome == nome,
                    Conta.usuario_id == usuario_id,
                    Conta.ativo.is_(True),
                )
            )
        )

        if exclude_id:
            query = select(
                exists().where(
                    and_(
                        Conta.nome == nome,
                        Conta.usuario_id == usuario_id,
                        Conta.ativo.is_(True),
                        Conta.id != exclude_id,
                    )
                )
            )

        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def _conta_tem_transacoes(db: AsyncSession, conta_id: int) -> bool:
        """Verifica se conta tem transações vinculadas"""
        query = select(
            exists().where(
                or_(
                    Transacao.conta_origem_id == conta_id,
                    Transacao.conta_destino_id == conta_id,
                )
            )
        )
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def _contar_contas_ativas(db: AsyncSession, usuario_id: int) -> int:
        """Conta quantas contas ativas o usuário tem"""
        result = await db.execute(
            select(func.count(Conta.id)).where(
                and_(Conta.usuario_id == usuario_id, Conta.ativo.is_(True))
            )
        )
        return result.scalar_one()

    @staticmethod
    async def _remover_conta_padrao(
        db: AsyncSession, usuario_id: int, exclude_id: int | None = None
    ) -> None:
        """Remove flag de conta padrão de todas as contas do usuário"""
        query = (
            update(Conta)
            .where(and_(Conta.usuario_id == usuario_id, Conta.conta_padrao.is_(True)))
            .values(conta_padrao=False)
        )

        if exclude_id:
            query = query.where(Conta.id != exclude_id)

        await db.execute(query)

    @staticmethod
    async def _definir_nova_conta_padrao(
        db: AsyncSession, usuario_id: int, exclude_id: int
    ) -> None:
        """Define uma nova conta padrão quando a atual é excluída"""
        result = await db.execute(
            select(Conta)
            .where(
                and_(
                    Conta.usuario_id == usuario_id,
                    Conta.ativo.is_(True),
                    Conta.id != exclude_id,
                )
            )
            .limit(1)
        )
        nova_conta = result.scalar_one_or_none()
        if nova_conta:
            nova_conta.conta_padrao = True
