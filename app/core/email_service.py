# app/core/email_service.py

import asyncio

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr, SecretStr

from app.core.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.SMTP_USER,
    MAIL_PASSWORD=SecretStr(config.SMTP_PASSWORD),
    MAIL_FROM=config.MAIL_FROM,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_SERVER=config.SMTP_SERVER,
    MAIL_PORT=int(config.SMTP_PORT),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,  # True para porta 465, False para 587
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,  # importante para validar o certificado SSL
)

fm = FastMail(conf)


def send_email_background(email_to: str, token: str) -> None:
    asyncio.run(send_confirmation_email(email_to, token))


async def send_email(subject: str, email_to: EmailStr, body: str) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype=MessageType.html,
    )
    await fm.send_message(message)


async def send_confirmation_email(email_to: EmailStr, token: str) -> None:
    html_content = f"""
        <h1>Código de Confirmação</h1>
        <p>Use o código abaixo para confirmar seu e-mail no aplicativo:</p>
        <h2 style="font-size: 24px; font-weight: bold;">{token}</h2>
        <p>Este código expira em 10 minutos.</p>
        <p>Se não foi você quem solicitou, ignore esta mensagem.</p>
    """

    message = MessageSchema(
        subject="Código de confirmação de e-mail",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html,
    )

    await fm.send_message(message)
