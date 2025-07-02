from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105


class LoginRequest(BaseModel):
    email: str
    password: str
    totp_token: str | None = None
