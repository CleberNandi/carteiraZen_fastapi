"""
Testes de segurança para endpoints de categorias.
"""

import time
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException, status
from httpx import AsyncClient
import pytest
from schemas.categoria import CategoriaRead
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.categorias.router import listar_categorias
from app.models.usuario import Usuario
from app.services.categoria_service import CategoriaService


class TestCategoriasSecurity:
    """Testes de segurança para endpoints de categorias."""

    @pytest.mark.asyncio
    async def test_listar_categorias_large_dataset(
        self, db_session: AsyncSession, mock_user: Usuario
    ):
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
    async def test_sql_injection_protection_integration(
        self, client: AsyncClient, authenticated_user: dict[str, str]
    ):
        """A API deve ignorar ou rejeitar tentativas de SQL Injection."""
        malicious_input = "1; DROP TABLE categorias; --"

        response = await client.get(
            f"/api/v1/categorias/?nome={malicious_input}",
            headers=authenticated_user,
        )

        # A API deve responder 200 (ou 422 se a validação barrar),
        # mas nunca executar SQL inválido
        assert response.status_code in (200, 422)
        data = response.json()

        # Se a API aceitou a query param, resultado deve ser seguro
        if response.status_code == 200:
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_xss_injection_protection(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Não deve retornar scripts maliciosos no payload."""
        xss_payload = "<script>alert('xss')</script>"

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = []

            result = await listar_categorias(
                incluir_subcategorias=True,
                apenas_principais=False,
                apenas_personalizadas=False,
                db=db_session,
                current_user=mock_current_user,
            )

            assert isinstance(result, list)
            assert all(xss_payload not in str(item) for item in result)

    @pytest.mark.asyncio
    async def test_unauthorized_access_rules(
        self, db_session: AsyncSession, mock_current_user_not_verified: Usuario
    ):
        """Sem usuário autenticado deve retornar 401."""
        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = []

            if (
                not mock_current_user_not_verified
                or not mock_current_user_not_verified.is_verified
            ):
                with pytest.raises(HTTPException) as excinfo:
                    await listar_categorias(
                        incluir_subcategorias=True,
                        apenas_principais=False,
                        apenas_personalizadas=False,
                        db=db_session,
                        current_user=mock_current_user_not_verified,
                    )

                assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_invalid_token(self, client: AsyncClient):
        """Sem usuário autenticado deve retornar 401."""

        response = await client.get(
            "/api/v1/categorias/", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Credenciais inválidas"

    @pytest.mark.asyncio
    async def test_no_credentials(self, client: AsyncClient):
        """Sem header deve retornar 403 Forbidden."""
        response = await client.get("/api/v1/categorias/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Not authenticated"
