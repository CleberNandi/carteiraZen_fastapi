from app.schemas.base import BaseSchema


class CategoriaBase(BaseSchema):
    ativo: bool | None = True
    descricao: str
    user_id: int


class CategoriaCreate(CategoriaBase):
    descricao: str


class CategoriaUpdate(CategoriaBase):
    ativo: bool | None = None


class CategoriaRead(CategoriaBase):
    id: int
