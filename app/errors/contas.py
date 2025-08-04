from .base import AppError

JA_EXISTE = AppError(
    code="conta_ja_existe",
    message_template="Já existe uma conta (ID: {id}) com esse {campo}.",
)

NAO_ENCONTRADA = AppError(
    code="conta_nao_encontrada", message_template="Conta não encontrada."
)

JA_DELETADA = AppError(
    code="conta_ja_deletada", message_template="Conta já foi deletada."
)

JA_ATIVA = AppError(code="conta_ja_ativa", message_template="Conta já está ativa.")

SALDO_NEGATIVO = AppError(
    code="conta_saldo_negativo",
    message_template="A operação resultaria em saldo negativo na conta.",
)

OPERACAO_INVALIDA = AppError(
    code="conta_operacao_invalida",
    message_template="Operação inválida para o tipo de conta.",
)
