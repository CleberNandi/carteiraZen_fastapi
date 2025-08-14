from app.schemas.base import BaseSchema


class CategoriaBase(BaseSchema):
    nome: str
    tipo: str
    cor: str
    ativo: bool = True
    usuario_id: int


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id: int
