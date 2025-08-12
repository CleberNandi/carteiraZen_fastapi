from datetime import datetime
from uuid import uuid4

from pydantic import EmailStr

from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    name: str
    email: str
    plan: str = "basic"
    sync_enabled: bool = True
    last_sync_at: datetime | None = None


class UserCreate(UserBase):
    hashed_password: str | None = None
    totp_secret: str | None = None
    ativo: bool = True
    is_superuser: bool = False
    is_2fa_enabled: bool = False
    sync_uuid: str = str(uuid4())


class UserOut(UserBase):
    id: int
    sync_uuid: str


class EmailConfirmRequest(BaseSchema):
    email: EmailStr
    token: str
