from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria as AuditoriaModel


def get_auditorias(
    db: Session,
    tabela: str | None = None,
    registro_id: int | None = None,
    acao: str | None = None,
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[AuditoriaModel]:
    query = db.query(AuditoriaModel)
    if tabela:
        query = query.filter(AuditoriaModel.tabela == tabela)
    if registro_id:
        query = query.filter(AuditoriaModel.registro_id == registro_id)
    if acao:
        query = query.filter(AuditoriaModel.acao == acao)
    if user_id:
        query = query.filter(AuditoriaModel.user_id == user_id)
    return query.order_by(AuditoriaModel.data.desc()).offset(skip).limit(limit).all()
