from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    name: str
    email: str
    plan: str = "basic"
    sync_enabled: bool = False


class UserCreate(UserBase):
    hashed_password: str | None = None
    totp_secret: str | None = None
    ativo: bool = True
    is_superuser: bool = False
    is_2fa_enabled: bool = False


class UserOut(UserBase):
    id: int
    sync_uuid: str
