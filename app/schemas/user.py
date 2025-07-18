from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    hashed_password: str | None = None
    totp_secret: str | None = None
    is_active: bool
    is_superuser: bool
    is_2fa_enabled: bool


class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
