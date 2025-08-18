from collections.abc import Awaitable, Callable
import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Import do Starlette (mais compatível)
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de segurança"""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()

        try:
            # Processa a requisição
            response = await call_next(request)
        except Exception:
            # Log de erros
            process_time = time.time() - start_time
            logger.exception(
                f"Error processing {request.method} {request.url.path} - {process_time:.3f}s"
            )
            raise
        else:
            # Adiciona headers de segurança
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers[
                "Permissions-Policy"
            ] = "geolocation=(), microphone=(), camera=()"
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains"

            # Log de requisições
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"{response.status_code} - {process_time:.3f}s - "
                f"IP: {request.client.host if request.client else 'unknown'}"
            )

            return response


# Middleware alternativo mais simples (caso o BaseHTTPMiddleware não funcione)
class SimpleSecurityMiddleware:
    """Middleware de segurança simplificado usando decorator"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                # Adiciona headers de segurança
                headers = dict(message.get("headers", []))

                security_headers = {
                    b"x-content-type-options": b"nosniff",
                    b"x-frame-options": b"DENY",
                    b"x-xss-protection": b"1; mode=block",
                    b"referrer-policy": b"strict-origin-when-cross-origin",
                    b"permissions-policy": b"geolocation=(), microphone=(), camera=()",
                    b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                }

                for key, value in security_headers.items():
                    if key not in headers:
                        headers[key] = value

                message["headers"] = list(headers.items())

                # Log da requisição
                method = scope.get("method", "UNKNOWN")
                path = scope.get("path", "/")
                process_time = time.time() - start_time

                logger.info(f"{method} {path} - {process_time:.3f}s")

            await send(message)

        await self.app(scope, receive, send_wrapper)
