"""
Testes de edge cases avançados para endpoints de categorias.
"""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.categorias.router import listar_categorias
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaRead
from app.services.categoria_service import CategoriaService


class TestCategoriasEdgeCases:
    """Testes de edge cases avançados para categorias."""

    @pytest.mark.asyncio
    async def test_listar_categorias_timeout(
        self, db_session: AsyncSession, mock_user: Usuario
    ):
        """Simula timeout no serviço."""
        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.side_effect = TimeoutError("Service timeout")

            with pytest.raises(TimeoutError, match="Service timeout"):
                await listar_categorias(
                    incluir_subcategorias=True,
                    apenas_principais=False,
                    apenas_personalizadas=False,
                    db=db_session,
                    current_user=mock_user,
                )

    @pytest.mark.asyncio
    async def test_listar_categorias_circular_reference(
        self, db_session: AsyncSession, mock_user: Usuario
    ):
        """Simula categorias em loop circular."""
        circular_categoria = CategoriaRead(
            id=1,
            nome="Categoria A",
            descricao="Teste",
            categoria_pai_id=1,
        )

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = [circular_categoria]

            result = await listar_categorias(
                incluir_subcategorias=True,
                apenas_principais=False,
                apenas_personalizadas=False,
                db=db_session,
                current_user=mock_user,
            )

            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].categoria_pai_id == 1

    @pytest.mark.asyncio
    async def test_listar_categorias_max_depth(
        self, db_session: AsyncSession, mock_user: Usuario
    ):
        """Simula árvore de categorias profunda (100 níveis) usando categoria_pai_id."""

        # Criar 100 categorias encadeadas via categoria_pai_id
        categorias = [
            CategoriaRead(
                id=0, nome="Raiz", descricao="Profundo", categoria_pai_id=None
            )
        ]
        for i in range(1, 100):
            categorias.append(
                CategoriaRead(
                    id=i,
                    nome=f"Categoria {i}",
                    descricao="Nivel profundo",
                    categoria_pai_id=i - 1,
                )
            )

        # Mock do listar para retornar a lista achatada
        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = categorias

            result = await listar_categorias(
                incluir_subcategorias=True,
                apenas_principais=False,
                apenas_personalizadas=False,
                db=db_session,
                current_user=mock_user,
            )

            assert isinstance(result, list)
            assert len(result) == 100

            # Verificar encadeamento via categoria_pai_id
            for i in range(1, len(result)):
                assert result[i].categoria_pai_id == result[i - 1].id
