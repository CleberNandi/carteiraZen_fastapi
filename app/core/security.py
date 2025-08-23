import base64
from datetime import UTC, datetime, timedelta
from enum import Enum
from io import BytesIO
import secrets
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import qrcode

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class SecurityManager:
    """Gerenciador central de segurança"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Gera hash da senha"""
        rounds = getattr(settings, "BCRYPT_ROUNDS", 12)
        return pwd_context.using(bcrypt__rounds=rounds).hash(password)

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """Valida força da senha"""
        min_length = getattr(settings, "PASSWORD_MIN_LENGTH", 8)

        if len(password) < min_length:
            return False, f"Senha deve ter pelo menos {min_length} caracteres"

        if not any(c.isupper() for c in password):
            return False, "Senha deve conter pelo menos uma letra maiúscula"

        if not any(c.islower() for c in password):
            return False, "Senha deve conter pelo menos uma letra minúscula"

        if not any(c.isdigit() for c in password):
            return False, "Senha deve conter pelo menos um número"

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Senha deve conter pelo menos um caractere especial"

        return True, "Senha válida"


class JWTManager:
    """Gerenciador de tokens JWT"""

    @staticmethod
    def create_access_token(data: dict[str, Any]) -> str:
        """Cria token de acesso"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(
            minutes=getattr(settings, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        )
        to_encode.update({"exp": expire, "type": "access"})

        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=getattr(settings, "JWT_ALGORITHM", "HS256"),
        )

    @staticmethod
    def create_refresh_token(data: dict[str, Any]) -> str:
        """Cria token de refresh"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(
            days=getattr(settings, "JWT_REFRESH_TOKEN_EXPIRE_DAYS", 30)
        )
        to_encode.update({"exp": expire, "type": "refresh"})

        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=getattr(settings, "JWT_ALGORITHM", "HS256"),
        )

    @staticmethod
    def verify_token(
        token: str, token_type: TokenType = TokenType.ACCESS
    ) -> dict[str, Any] | None:
        """Verifica e decodifica token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[getattr(settings, "JWT_ALGORITHM", "HS256")],
            )
        except JWTError:
            return None
        else:
            if payload.get("type") != token_type:
                return None
            return payload


class TOTPManager:
    """Gerenciador de 2FA TOTP"""

    @staticmethod
    def generate_secret() -> str:
        """Gera secret para 2FA"""
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(email: str, secret: str) -> str:
        """Gera QR code para 2FA (retorna base64)"""
        issuer = getattr(settings, "TOTP_ISSUER_NAME", "Zenny")
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=email, issuer_name=issuer)

        # Gera QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Converte para base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")  # type: ignore
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verifica código TOTP"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

    @staticmethod
    def get_backup_codes() -> list[str]:
        """Gera códigos de backup"""
        return [secrets.token_hex(4).upper() for _ in range(10)]
