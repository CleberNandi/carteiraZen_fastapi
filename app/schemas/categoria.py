from pydantic import BaseModel, ConfigDict


class CategoriaBase(BaseModel):
    ativo: bool | None = True
    descricao: str


class CategoriaCreate(CategoriaBase):
    descricao: str
    user_id: int


class CategoriaUpdate(CategoriaBase):
    ativo: bool | None = None


class CategoriaRead(CategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
