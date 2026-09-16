from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from schemas.gasto import EvolucaoGastoResponse
from schemas.orcamento import ComparativoOrcamentoResponse
from schemas.relatorio import (
    GastoCategoria,
    GastoMensalResponse,
    Periodo,
    RelatorioResponse,
    Resumo,
)
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models import categoria, fatura, orcamento, transacao, usuario

Categoria = categoria.Categoria
Fatura = fatura.Fatura
Orcamento = orcamento.Orcamento
Transacao = transacao.Transacao
Usuario = usuario.Usuario

router = APIRouter()


@router.get("/dashboard", response_model=RelatorioResponse)
def obter_dashboard(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
    ano: int | None = None,
    mes: int | None = None,
    *,
    mes_atual: bool = True,
) -> RelatorioResponse:
    """Obtém dados para o dashboard principal"""
    if mes_atual or not ano or not mes:
        hoje = date.today()
        ano = hoje.year
        mes = hoje.month

    # Gastos do mês por categoria
    gastos_categoria = (
        db.query(
            Categoria.nome, Categoria.cor, func.sum(Transacao.valor).label("total")
        )
        .join(Transacao, Categoria.id == Transacao.categoria_id)
        .filter(
            Transacao.usuario_id == current_user.id,
            extract("year", Transacao.data_transacao) == ano,
            extract("month", Transacao.data_transacao) == mes,
        )
        .group_by(Categoria.id, Categoria.nome, Categoria.cor)
        .all()
    )

    # Total gasto no mês
    total_gasto_mes = db.query(func.sum(Transacao.valor)).filter(
        Transacao.usuario_id == current_user.id,
        extract("year", Transacao.data_transacao) == ano,
        extract("month", Transacao.data_transacao) == mes,
    ).scalar() or Decimal("0.00")

    # Faturas pendentes
    faturas_pendentes = (
        db.query(Fatura)
        .filter(Fatura.usuario_id == current_user.id, ~Fatura.paga)
        .count()
    )

    # Valor total das faturas pendentes
    valor_faturas_pendentes = db.query(
        func.sum(Fatura.valor_total - Fatura.valor_pago)
    ).filter(Fatura.usuario_id == current_user.id, ~Fatura.paga).scalar() or Decimal(
        "0.00"
    )

    # Orçamentos excedidos
    orcamentos_excedidos = (
        db.query(Orcamento)
        .filter(
            Orcamento.usuario_id == current_user.id,
            Orcamento.ano == ano,
            Orcamento.mes == mes,
            Orcamento.valor_gasto > Orcamento.valor_limite,
            Orcamento.ativo.is_(True),
        )
        .count()
    )

    # Total orçado vs gasto
    total_orcado = db.query(func.sum(Orcamento.valor_limite)).filter(
        Orcamento.usuario_id == current_user.id,
        Orcamento.ano == ano,
        Orcamento.mes == mes,
        Orcamento.ativo.is_(True),
    ).scalar() or Decimal("0.00")

    # Últimas transações
    ultimas_transacoes = (
        db.query(Transacao)
        .filter(Transacao.usuario_id == current_user.id)
        .order_by(Transacao.data_transacao.desc())
        .limit(10)
        .all()
    )

    return RelatorioResponse(
        periodo=Periodo(ano=ano, mes=mes),
        resumo=Resumo(
            total_gasto_mes=total_gasto_mes,
            faturas_pendentes=faturas_pendentes,
            valor_faturas_pendentes=valor_faturas_pendentes,
            orcamentos_excedidos=orcamentos_excedidos,
            total_orcado=total_orcado,
            percentual_orcamento_usado=float(
                (total_gasto_mes / total_orcado * 100) if total_orcado > 0 else 0
            ),
        ),
        gastos_por_categoria=[
            GastoCategoria(
                categoria=gasto.nome,
                cor=gasto.cor,
                valor=gasto.total,
                percentual=float(
                    (gasto.total / total_gasto_mes * 100) if total_gasto_mes > 0 else 0
                ),
            )
            for gasto in gastos_categoria
        ],
        ultimas_transacoes=[t.__dict__ for t in ultimas_transacoes],
    )


@router.get("/gastos-mensais", response_model=list[GastoMensalResponse])
def obter_gastos_mensais(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
    ano: int = Query(default=datetime.now().year),
    categoria_id: int | None = None,
) -> list[GastoMensalResponse]:
    """Obtém gastos mensais do ano para gráfico"""
    query = db.query(
        extract("month", Transacao.data_transacao).label("mes"),
        func.sum(Transacao.valor).label("total"),
    ).filter(
        Transacao.usuario_id == current_user.id,
        extract("year", Transacao.data_transacao) == ano,
    )

    if categoria_id:
        query = query.filter(Transacao.categoria_id == categoria_id)

    gastos = (
        query.group_by(extract("month", Transacao.data_transacao))
        .order_by(extract("month", Transacao.data_transacao))
        .all()
    )

    # Preenche meses sem gastos com 0
    meses_nomes = [
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    ]
    gastos_dict = {int(gasto.mes): float(gasto.total) for gasto in gastos}

    return [
        GastoMensalResponse(
            mes=i, nome=meses_nomes[i - 1], valor=gastos_dict.get(i, 0.0)
        )
        for i in range(1, 13)
    ]


@router.get(
    "/comparativo-orcamentos", response_model=list[ComparativoOrcamentoResponse]
)
def obter_comparativo_orcamentos(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
    ano: int = Query(default=datetime.now().year),
    mes: int = Query(default=datetime.now().month),
) -> list[ComparativoOrcamentoResponse]:
    """Compara orçado vs gasto por categoria"""
    orcamentos = (
        db.query(
            Orcamento,
            Categoria.nome.label("categoria_nome"),
            Categoria.cor.label("categoria_cor"),
        )
        .join(Categoria, Orcamento.categoria_id == Categoria.id)
        .filter(
            Orcamento.usuario_id == current_user.id,
            Orcamento.ano == ano,
            Orcamento.mes == mes,
            Orcamento.ativo.is_(True),
        )
        .all()
    )

    return [
        ComparativoOrcamentoResponse(
            categoria=categoria_nome,
            cor=categoria_cor,
            valor_orcado=float(orcamento.valor_limite),
            valor_gasto=float(orcamento.valor_gasto),
            valor_disponivel=float(orcamento.valor_disponivel),
            percentual_usado=orcamento.percentual_usado,
            excedeu=orcamento.excedeu_limite,
            status="excedido"
            if orcamento.excedeu_limite
            else "alerta"
            if orcamento.deve_notificar
            else "ok",
        )
        for orcamento, categoria_nome, categoria_cor in orcamentos
    ]


@router.get("/evolucao-gastos", response_model=list[EvolucaoGastoResponse])
def obter_evolucao_gastos(
    db: Session = Depends(get_async_db),
    current_user: Usuario = Depends(get_current_user),
    meses: int = Query(default=6, ge=3, le=24),
) -> list[EvolucaoGastoResponse]:
    """Obtém evolução dos gastos nos últimos meses"""
    hoje = date.today()

    # Calcula os últimos N meses
    gastos: list[EvolucaoGastoResponse] = []
    for i in range(meses):
        if hoje.month - i <= 0:
            ano = hoje.year - 1
            mes_calc = 12 + (hoje.month - i)
        else:
            ano = hoje.year
            mes_calc = hoje.month - i

        total_mes = db.query(func.sum(Transacao.valor)).filter(
            Transacao.usuario_id == current_user.id,
            extract("year", Transacao.data_transacao) == ano,
            extract("month", Transacao.data_transacao) == mes_calc,
        ).scalar() or Decimal("0.00")

        gastos.insert(
            0,
            EvolucaoGastoResponse(
                ano=ano,
                mes=mes_calc,
                valor=float(total_mes),
                periodo=f"{mes_calc:02d}/{ano}",
            ),
        )

    return gastos
