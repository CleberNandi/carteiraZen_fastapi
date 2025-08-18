from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

BEARER_TOKEN_TYPE = "bearer"  # noqa: S105


class UserRegister(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLogin2FA(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None
    backup_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = BEARER_TOKEN_TYPE
    expires_in: int
    requires_2fa: bool = False


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class Enable2FARequest(BaseModel):
    totp_code: str


class Verify2FARequest(BaseModel):
    totp_code: str | None = None
    backup_code: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class UserProfile(BaseModel):
    id: int
    nome: str
    email: str
    is_verified: bool
    is_2fa_enabled: bool
    plan: str | None
    last_login: datetime | None
    created_at: datetime


class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list[str]


class DeviceInfo(BaseModel):
    session_id: str
    device_info: str | None
    ip_address: str | None
    user_agent: str | None
    last_activity: datetime
    is_current: bool
