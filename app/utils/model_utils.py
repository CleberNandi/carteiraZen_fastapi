from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


def apply_update_fields(
    model: DeclarativeBase,
    data: BaseModel,
    fields: list[str],
    *,
    ignore_none: bool = True,
) -> list[str]:
    """
    Atualiza campos de um modelo baseado em um schema e retorna os campos alterados.

    - model: instância do SQLAlchemy model.
    - data: instância do Pydantic schema (como ContaUpdate).
    - fields: lista de campos permitidos para atualização.
    - ignore_none: se True, campos com valor None serão ignorados.
    """
    atualizados: list[str] = []

    for field in fields:
        if not hasattr(model, field):
            continue

        # ⚠️ Só atualiza se o campo foi explicitamente enviado
        if field not in data.model_fields_set:
            continue

        valor_novo = getattr(data, field)
        if ignore_none and valor_novo is None:
            continue

        valor_atual = getattr(model, field)
        if valor_novo != valor_atual:
            setattr(model, field, valor_novo)
            atualizados.append(field)

    return atualizados
