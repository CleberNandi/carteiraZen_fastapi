import json
from typing import Any

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, Session

from app import models

Auditoria = models.Auditoria


def serialize_mapped(model: DeclarativeBase) -> dict[str, Any]:
    """
    Serializa apenas os atributos mapeados no SQLAlchemy.
    Evita incluir campos internos como _sa_instance_state.
    """
    return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}


def registrar_auditoria(
    db: Session,
    tabela: str,
    registro_id: int,
    acao: str,
    user_id: int,
    dados_antes: dict[str, Any] | None = None,
    dados_input: dict[str, Any] | None = None,
    dados_depois: dict[str, Any] | None = None,
) -> None:
    auditoria = Auditoria(
        tabela=tabela,
        registro_id=registro_id,
        acao=acao,
        user_id=user_id,
        dados_antes=json.dumps(dados_antes, default=str, ensure_ascii=False)
        if dados_antes
        else None,
        dados_input=json.dumps(dados_input, default=str, ensure_ascii=False)
        if dados_input
        else None,
        dados_depois=json.dumps(dados_depois, default=str, ensure_ascii=False)
        if dados_depois
        else None,
    )
    db.add(auditoria)
