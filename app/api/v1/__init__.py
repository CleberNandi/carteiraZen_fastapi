# Inicializa o pacote v1

from .banco_endpoints import router as banco_router
from .endpoints import router as user_router

__all__ = ["banco_router", "user_router"]
