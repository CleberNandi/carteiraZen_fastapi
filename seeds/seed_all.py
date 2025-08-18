from collections.abc import Callable, Coroutine
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.seed_bancos import seed_bancos
from app.utils.seed_categorias import seed_categorias

# Lista de funções de seed async
ALL_SEEDS: list[Callable[[AsyncSession], Coroutine[Any, Any, None]]] = [
    seed_categorias,
    seed_bancos,
]


async def run_all_seeds(session: AsyncSession) -> None:
    """Executa todos os seeds registrados"""
    for seed_func in ALL_SEEDS:
        await seed_func(session)
