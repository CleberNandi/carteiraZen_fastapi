from .base import AppError

JA_EXISTE = AppError(
    code="banco_ja_existe",
    message_template="Já existe um banco (ID: {id}) com esse {campo}.",
)

NAO_ENCONTRADO = AppError(
    code="banco_nao_encontrado", message_template="Banco não encontrado."
)

JA_DESATIVADO = AppError(
    code="banco_ja_desativado", message_template="Banco (ID: {id}) já foi desativado."
)

JA_ATIVO = AppError(code="banco_ja_ativo", message_template="Banco já está ativo.")
