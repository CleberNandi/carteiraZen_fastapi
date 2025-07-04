from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoriaBase(BaseModel):
    ativo: bool | None = True


class CategoriaCreate(CategoriaBase):
    user_id: int  # será necessário apenas se o admin estiver criando para outro usuário


class CategoriaUpdate(CategoriaBase):
    ativo: bool | None = None


class CategoriaRead(BaseModel):
    id: int
    ativo: bool
    user_id: int
    created_at: datetime | None = None
    created_by: int | None = None
    updated_at: datetime | None = None
    updated_by: int | None = None
    deleted_at: datetime | None = None
    deleted_by: int | None = None

    model_config = ConfigDict(from_attributes=True)
