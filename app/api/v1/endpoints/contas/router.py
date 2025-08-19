# app/routers/conta.py

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_active_user
from app.models.usuario import Usuario
from app.schemas.conta import (
    ContaCreate,
    ContaListResponse,
    ContaRead,
    ContaUpdate,
    TipoConta,
)
from app.services.conta_service import ContaService

router = APIRouter()


@router.post("/", response_model=ContaRead, status_code=status.HTTP_201_CREATED)
async def criar_conta(
    conta_in: ContaCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_active_user),
) -> ContaRead:
    """
    Cria uma nova conta para o usuário autenticado.

    - **nome**: Nome da conta (obrigatório)
    - **tipo**: Tipo da conta (CORRENTE, POUPANCA, INVESTIMENTO, CARTEIRA, OUTRO)
    - **saldo_cents**: Saldo inicial em centavos (opcional, padrão: 0)
    - **cheque_especial_cents**: Limite do cheque especial em centavos (opcional, padrão: 0)
    - **cor**: Cor em formato hexadecimal (obrigatório)
    - **incluir_na_soma_inicial**: Se deve incluir no saldo total (opcional, padrão: true)
    - **conta_padrao**: Se é a conta padrão (opcional, padrão: false)
    - **banco_id**: ID do banco (opcional)
    """
    return await ContaService.criar(db, conta_in, current_user)


@router.get("/", response_model=ContaListResponse)
async def listar_contas(
    skip: int = Query(default=0, ge=0, description="Número de registros para pular"),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Número máximo de registros"
    ),
    tipo: TipoConta
    | None = Query(default=None, description="Filtrar por tipo de conta"),
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_active_user),
    *,
    incluir_inativas: bool = Query(
        default=False, description="Incluir contas inativas"
    ),
) -> ContaListResponse:
    """
    Lista todas as contas do usuário autenticado com filtros opcionais.

    Retorna uma lista paginada com resumo financeiro.
    """
    return await ContaService.listar(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        incluir_inativas=incluir_inativas,
        tipo_filter=tipo.value if tipo else None,
    )


@router.get("/{conta_id}", response_model=ContaRead)
async def buscar_conta(
    conta_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_active_user),
) -> ContaRead:
    """
    Busca uma conta específica por ID.

    Retorna os detalhes completos da conta, incluindo saldos calculados.
    """
    return await ContaService.buscar_por_id(db, conta_id, current_user)


@router.put("/{conta_id}", response_model=ContaRead)
async def atualizar_conta(
    conta_id: int,
    data: ContaUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_active_user),
) -> ContaRead:
    """
    Atualiza dados da conta.

    **Nota**: O saldo não pode ser editado diretamente, apenas através de transações.
    """
    return await ContaService.atualizar(db, conta_id, data, current_user)


@router.delete("/{conta_id}")
async def excluir_conta(
    conta_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_active_user),
) -> dict[str, bool]:
    """
    Exclui uma conta (soft delete).

    **Validações**:
    - Não pode excluir se existem transações vinculadas
    - Não pode excluir a única conta ativa
    - Se for conta padrão, automaticamente define outra como padrão
    """
    return await ContaService.excluir(db, conta_id, current_user)


@router.patch("/{conta_id}/definir-padrao", response_model=ContaRead)
async def definir_conta_padrao(
    conta_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_active_user),
) -> ContaRead:
    """
    Define uma conta como padrão para transações.

    Remove automaticamente a flag de padrão das outras contas.
    """
    return await ContaService.definir_como_padrao(db, conta_id, current_user)
