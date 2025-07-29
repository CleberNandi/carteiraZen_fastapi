from app.schemas.base import BaseSchema


class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"  # noqa: S105


class LoginRequest(BaseSchema):
    email: str
    password: str
    totp_token: str | None = None
