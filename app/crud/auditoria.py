from collections.abc import Sequence

from sqlalchemy.orm import Session

from app import models

Auditoria = models.Auditoria


def get_auditorias(
    db: Session,
    tabela: str | None = None,
    registro_id: int | None = None,
    acao: str | None = None,
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Auditoria]:
    query = db.query(Auditoria)
    if tabela:
        query = query.filter(Auditoria.tabela == tabela)
    if registro_id:
        query = query.filter(Auditoria.registro_id == registro_id)
    if acao:
        query = query.filter(Auditoria.acao == acao)
    if user_id:
        query = query.filter(Auditoria.user_id == user_id)
    return query.order_by(Auditoria.data.desc()).offset(skip).limit(limit).all()
