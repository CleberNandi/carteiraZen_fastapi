from unittest.mock import AsyncMock, patch

from fastapi import status
from httpx import AsyncClient
import pytest

from app.schemas.categoria import CategoriaRead
from app.services.categoria_service import Categoria, CategoriaService


class TestCategoriasRouterIntegration:
    """Testes de integração para o router de categorias."""

    @pytest.mark.asyncio
    async def test_integration_listar_categorias(
        self,
        client: AsyncClient,
        sample_categoria_read: CategoriaRead,
        authenticated_user: dict[str, str],
    ):
        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = [sample_categoria_read]

            # 5️⃣ Chamar endpoint com token no header
            response = await client.get(
                "/api/v1/categorias/", headers=authenticated_user
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["nome"] == "Alimentação"

    @pytest.mark.asyncio
    async def test_integration_listar_categorias_with_params(
        self,
        client: AsyncClient,
        authenticated_user: dict[str, str],
    ):
        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = []

            response = await client.get(
                "/api/v1/categorias/",
                headers=authenticated_user,
                params={
                    "incluir_subcategorias": False,
                    "apenas_principais": True,
                    "apenas_personalizadas": True,
                },
            )

            assert response.status_code == status.HTTP_200_OK
            mock_listar.assert_called_once()

    @pytest.mark.asyncio
    async def test_integration_obter_categoria(
        self,
        client: AsyncClient,
        sample_categoria_model: Categoria,
        authenticated_user: dict[str, str],
    ):
        with patch.object(
            CategoriaService, "obter", new_callable=AsyncMock
        ) as mock_obter:
            mock_obter.return_value = sample_categoria_model

            response = await client.get(
                "/api/v1/categorias/1", headers=authenticated_user
            )
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_integration_listar_subcategorias(
        self,
        client: AsyncClient,
        sample_categoria_read: CategoriaRead,
        authenticated_user: dict[str, str],
    ):
        with patch.object(
            CategoriaService, "listar_subcategorias", new_callable=AsyncMock
        ) as mock_listar_sub:
            mock_listar_sub.return_value = [sample_categoria_read]

            response = await client.get(
                "/api/v1/categorias/1/subcategorias", headers=authenticated_user
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1

    @pytest.mark.asyncio
    async def test_integration_criar_categoria(
        self,
        client: AsyncClient,
        sample_categoria_model: Categoria,
        authenticated_user: dict[str, str],
    ):
        categoria_data = {
            "nome": "Nova Categoria",
            "descricao": "Descrição nova",
            "categoria_pai_id": None,
        }

        with patch.object(
            CategoriaService, "criar", new_callable=AsyncMock
        ) as mock_criar:
            mock_criar.return_value = sample_categoria_model

            response = await client.post(
                "/api/v1/categorias/", headers=authenticated_user, json=categoria_data
            )
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_integration_atualizar_categoria(
        self,
        client: AsyncClient,
        sample_categoria_model: Categoria,
        authenticated_user: dict[str, str],
    ):
        categoria_data = {
            "nome": "Atualizada",
            "descricao": "Nova descrição",
            "categoria_pai_id": None,
        }

        with patch.object(
            CategoriaService, "atualizar", new_callable=AsyncMock
        ) as mock_atualizar:
            mock_atualizar.return_value = sample_categoria_model

            response = await client.put(
                "/api/v1/categorias/1", headers=authenticated_user, json=categoria_data
            )
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_integration_excluir_categoria(
        self, client: AsyncClient, authenticated_user: dict[str, str]
    ):
        with patch.object(
            CategoriaService, "excluir", new_callable=AsyncMock
        ) as mock_excluir:
            mock_excluir.return_value = {"ok": True}

            response = await client.delete(
                "/api/v1/categorias/1", headers=authenticated_user
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["ok"] is True
