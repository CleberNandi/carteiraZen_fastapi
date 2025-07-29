from app.schemas.base import BaseSchema


class CartaoBase(BaseSchema):
    numero: str  # Número do cartão (mascarado)
    nome_impresso: str  # Nome impresso no cartão
    validade: str  # Validade do cartão (formato YYYY-MM)
    bandeira: str  # Bandeira do cartão (Visa, MasterCard, etc.)
    limite: int  # Limite do cartão em centavos ou outra unidade
    banco_id: int  # ID do banco relacionado
    user_id: int  # ID do usuário dono do cartão
    ativo: bool = True  # Indica se o cartão está ativo


class CartaoCreate(CartaoBase):
    pass


class Cartao(CartaoBase):
    id: int  # ID do cartão
