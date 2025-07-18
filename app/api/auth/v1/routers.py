import io

import pyotp
import qrcode
from core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
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

    if not user or not verify_password(request.password, user.hashed_password):
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
