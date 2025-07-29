from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    name: str
    email: str


class UserCreate(UserBase):
    hashed_password: str | None = None
    totp_secret: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_2fa_enabled: bool = False


class UserOut(UserBase):
    id: int
