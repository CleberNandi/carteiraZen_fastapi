from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.orcamento_service import OrcamentoService
from sqlalchemy.orm import Session

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models import orcamento, usuario
from app.schemas.orcamento import (
    OrcamentoCreate,
    OrcamentoResponse,
    OrcamentosAlertaResponse,
    OrcamentosExcedidosResponse,
    OrcamentoUpdate,
    ResumoOrcamentosResponse,
)

Orcamento = orcamento.Orcamento
Usuario = usuario.Usuario

router = APIRouter()


@router.post("/", response_model=OrcamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_orcamento(
    orcamento_data: OrcamentoCreate,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> Orcamento:
    """Cria um novo orçamento"""
    try:
        return OrcamentoService.criar_orcamento(
            db=db,
            usuario_id=current_user.id,
            categoria_id=orcamento_data.categoria_id,
            ano=orcamento_data.ano,
            mes=orcamento_data.mes,
            valor_limite=orcamento_data.valor_limite,
            notificar_em=orcamento_data.notificar_em,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/", response_model=list[OrcamentoResponse])
def listar_orcamentos(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    ano: int | None = None,
    mes: int | None = None,
    categoria_id: int | None = None,
    *,
    apenas_ativos: bool = True,
    apenas_excedidos: bool = False,
) -> list[Orcamento]:
    """Lista os orçamentos do usuário"""
    query = db.query(Orcamento).filter(Orcamento.usuario_id == current_user.id)

    if ano:
        query = query.filter(Orcamento.ano == ano)

    if mes:
        query = query.filter(Orcamento.mes == mes)

    if categoria_id:
        query = query.filter(Orcamento.categoria_id == categoria_id)

    if apenas_ativos:
        query = query.filter(Orcamento.ativo.is_(True))

    orcamentos = query.offset(skip).limit(limit).all()

    if apenas_excedidos:
        orcamentos = [o for o in orcamentos if o.excedeu_limite]

    return orcamentos


@router.get("/{orcamento_id}", response_model=OrcamentoResponse)
def obter_orcamento(
    orcamento_id: int,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> Orcamento:
    """Obtém detalhes de um orçamento específico"""
    orcamento = (
        db.query(Orcamento)
        .filter(Orcamento.id == orcamento_id, Orcamento.usuario_id == current_user.id)
        .first()
    )

    if not orcamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado"
        )

    return orcamento


@router.put("/{orcamento_id}", response_model=OrcamentoResponse)
def atualizar_orcamento(
    orcamento_id: int,
    orcamento_data: OrcamentoUpdate,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> Orcamento:
    """Atualiza um orçamento existente"""
    orcamento = (
        db.query(Orcamento)
        .filter(Orcamento.id == orcamento_id, Orcamento.usuario_id == current_user.id)
        .first()
    )

    if not orcamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado"
        )

    # Atualiza campos fornecidos
    update_data = orcamento_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(orcamento, field, value)

    # Recalcula valor disponível se o limite mudou
    if orcamento_data.valor_limite is not None:
        orcamento.valor_disponivel = max(
            0, orcamento.valor_limite - orcamento.valor_gasto
        )

    db.commit()
    db.refresh(orcamento)
    return orcamento


@router.delete("/{orcamento_id}")
def excluir_orcamento(
    orcamento_id: int,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, str]:
    """Exclui um orçamento (soft delete - marca como inativo)"""
    orcamento = (
        db.query(Orcamento)
        .filter(Orcamento.id == orcamento_id, Orcamento.usuario_id == current_user.id)
        .first()
    )

    if not orcamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado"
        )

    orcamento.ativo = False
    db.commit()

    return {"message": "Orçamento excluído com sucesso"}


@router.get("/resumo/{ano}/{mes}", response_model=ResumoOrcamentosResponse)
def obter_resumo_orcamentos(
    ano: int,
    mes: int,
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, str | int | float]:
    """Obtém resumo dos orçamentos de um período"""
    return OrcamentoService.obter_resumo_orcamentos(
        db=db, usuario_id=current_user.id, ano=ano, mes=mes
    )


@router.get("/alertas/excedidos", response_model=OrcamentosExcedidosResponse)
def obter_orcamentos_excedidos(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict[str, int | list[Orcamento]]:
    """Obtém orçamentos que excederam o limite"""
    orcamentos_excedidos = OrcamentoService.obter_orcamentos_excedidos(
        db=db, usuario_id=current_user.id
    )

    return {
        "total_excedidos": len(orcamentos_excedidos),
        "valor_total_excesso": sum(
            o.valor_gasto - o.valor_limite for o in orcamentos_excedidos
        ),
        "orcamentos": orcamentos_excedidos,
    }


@router.get("/alertas/notificacoes", response_model=OrcamentosAlertaResponse)
def obter_orcamentos_para_notificar(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
) -> OrcamentosAlertaResponse:
    """Obtém orçamentos que devem gerar alertas"""
    orcamentos_alerta = OrcamentoService.obter_orcamentos_para_notificar(
        db=db, usuario_id=current_user.id
    )

    return OrcamentosAlertaResponse(
        total_alertas=len(orcamentos_alerta),
        orcamentos=[OrcamentoResponse.model_validate(o) for o in orcamentos_alerta],
    )
