from app.schemas.base import BaseSchema


class UsuarioBase(BaseSchema):
    nome: str
    email: str
    plan: str | None = "Basic"
    is_superuser: bool = False
    is_2fa_enabled: bool = False
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    password_hashed: str


class UsuarioRead(UsuarioBase):
    id: int
