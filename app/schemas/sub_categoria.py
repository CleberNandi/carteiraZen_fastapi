from app.schemas.base import BaseSchema


class SubCategoriaBase(BaseSchema):
    nome: str
    tipo: str
    cor: str
    ativo: bool = True
    categoria_id: int
    usuario_id: int


class SubCategoriaCreate(SubCategoriaBase):
    pass


class SubCategoriaRead(SubCategoriaBase):
    id: int
