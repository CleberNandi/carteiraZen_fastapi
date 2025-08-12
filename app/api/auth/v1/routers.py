from datetime import UTC, datetime, timedelta
import io

from core.dependencies import get_current_user
from core.email_service import send_email_background
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
import pyotp
import qrcode
from schemas.user import EmailConfirmRequest
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    generate_friendly_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User as User
from app.schemas.token import LoginRequest, Token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    user = db.query(User).filter(User.email == request.email).first()

    if not user or user.hashed_password is None:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if user.is_2fa_enabled:
        if not request.totp_token:
            raise HTTPException(status_code=400, detail="Token 2FA é obrigatório")

        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(request.totp_token):
            raise HTTPException(status_code=401, detail="Token 2FA inválido")

    access_token = create_access_token(data={"id": user.id, "sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/enable-2fa")
def enable_2fa(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> StreamingResponse:
    if current_user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA já habilitado")

    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    current_user.is_2fa_enabled = True
    db.commit()
    db.refresh(current_user)

    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email, issuer_name="CarteiraZen"
    )
    img = qrcode.make(otp_uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.post("/request-email")
def request_email(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    user = db.query(User).filter(User.email == email.lower()).first()

    if user and user.is_email_confirmed:
        raise HTTPException(
            status_code=400, detail="E-mail já confirmado. Por favor, faça login."
        )

    if not user:
        user = User(email=email.lower())
        db.add(user)

    # Gera token e salva com expiração (10 minutos)
    token = generate_friendly_token()
    user.email_confirmation_token = token
    user.email_token_expires_at = datetime.now(UTC) + timedelta(minutes=10)
    user.is_email_confirmed = False
    db.commit()

    background_tasks.add_task(send_email_background, user.email, token)

    return {"message": "Código enviado para o e-mail."}


@router.post("/confirm-email")
def confirm_email(
    data: EmailConfirmRequest,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if user.email_confirmation_token != data.token:
        raise HTTPException(status_code=400, detail="Token inválido")

    if user.email_token_expires_at and user.email_token_expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Token expirado")

    user.is_email_confirmed = True
    user.email_confirmation_token = None
    user.email_token_expires_at = None
    db.commit()
    return {"message": "E-mail confirmado com sucesso"}


@router.post("/create-password")
def create_password(
    email: str,
    password: str,
    confirm_password: str,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Senhas não conferem")

    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or not user.is_email_confirmed:
        raise HTTPException(status_code=400, detail="Usuário não confirmado")

    user.hashed_password = get_password_hash(password)
    db.commit()
    return {"message": "Senha criada com sucesso"}
