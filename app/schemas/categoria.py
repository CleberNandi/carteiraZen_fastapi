from app.schemas.base import BaseSchema


class CategoriaBase(BaseSchema):
    nome: str
    descricao: str | None = None
    icone: str = "help-circle"
    categoria_pai_id: int | None = None
    cor: str = "#C9F5FF"


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id: int
