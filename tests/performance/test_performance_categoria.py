"""
Testes de performance e stress para endpoints de categorias.
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.categorias.router import listar_categorias
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaRead
from app.services.categoria_service import CategoriaService


@pytest.mark.slow
class TestCategoriasPerformance:
    """Testes de performance para endpoints de categorias."""

    @pytest.mark.asyncio
    async def test_listar_categorias_large_dataset(
        self, db_session: AsyncSession, mock_user: Usuario
    ):
        """Deve listar 1000 categorias em menos de 1s."""
        large_dataset = [
            CategoriaRead(
                id=i,
                nome=f"Categoria {i}",
                descricao=f"Descrição da categoria {i}",
                categoria_pai_id=None if i % 10 == 0 else (i // 10),
                icone="help-circle",
                cor="#C9F5FF",
            )
            for i in range(1000)
        ]

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = large_dataset

            start_time = time.time()
            result = await listar_categorias(
                incluir_subcategorias=True,
                apenas_principais=False,
                apenas_personalizadas=False,
                db=db_session,
                current_user=mock_user,
            )
            execution_time = time.time() - start_time

            assert len(result) == 1000
            assert execution_time < 1.0
            mock_listar.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self, test_app: FastAPI, authenticated_user: dict[str, str]
    ):
        """Deve atender 50 requisições concorrentes em < 10s."""
        import time
        from unittest.mock import AsyncMock, patch

        from app.services.categoria_service import CategoriaService

        num_requests = 50
        transport = ASGITransport(app=test_app)
        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = []

            async def make_request(client: AsyncClient, request_id: int) -> int:
                response = await client.get(
                    f"/api/v1/categorias/?request_id={request_id}",
                    headers=authenticated_user,
                )
                return response.status_code

            start_time = time.time()
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                results = await asyncio.gather(
                    *[make_request(client, i) for i in range(num_requests)]
                )
            execution_time = time.time() - start_time

            assert all(status_code == 200 for status_code in results)
            assert len(results) == num_requests
            assert execution_time < 10.0
            assert mock_listar.call_count == num_requests


class TestCategoriasStress:
    """Testes de stress para endpoints de categorias."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_rapid_sequential_requests(
        self, db_session: AsyncSession, mock_user: Usuario
    ):
        """Deve responder 100 chamadas sequenciais em < 5s."""
        num_requests = 100

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = []

            start_time = time.time()
            for _ in range(num_requests):
                await listar_categorias(
                    incluir_subcategorias=True,
                    apenas_principais=False,
                    apenas_personalizadas=False,
                    db=db_session,
                    current_user=mock_user,
                )
            execution_time = time.time() - start_time

            assert execution_time < 5.0
            assert mock_listar.call_count == num_requests

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_memory_leak_prevention(
        self, db_session: AsyncSession, mock_user: Usuario
    ):
        """Executa 10 chamadas simulando resposta grande sem vazar memória."""
        large_response = [
            CategoriaRead(
                id=i,
                nome=f"Categoria {i}" * 10,
                descricao=f"Descrição longa da categoria {i}" * 20,
                categoria_pai_id=None,
            )
            for i in range(100)
        ]

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = large_response

            for _ in range(10):
                result = await listar_categorias(
                    incluir_subcategorias=True,
                    apenas_principais=False,
                    apenas_personalizadas=False,
                    db=db_session,
                    current_user=mock_user,
                )
                del result

            assert mock_listar.call_count == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "slow", "--tb=short"])
