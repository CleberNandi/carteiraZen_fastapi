import asyncio
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException, status
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.categorias.router import (
    atualizar_categoria,
    criar_categoria_personalizada,
    excluir_categoria,
    listar_categorias,
    listar_subcategorias,
    obter_categoria,
)
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaCreate, CategoriaRead
from app.services.categoria_service import Categoria, CategoriaService


class TestCategoriasRouterUnit:
    """Testes unitários para o router de categorias."""

    @pytest.mark.asyncio
    async def test_listar_categorias_success(
        self,
        db_session: AsyncSession,
        mock_current_user: Usuario,
        sample_categoria_read: CategoriaRead,
    ):
        """Deve listar categorias com sucesso."""
        # Arrange
        expected_categorias = [sample_categoria_read]

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = expected_categorias

            # Act
            result = await listar_categorias(
                incluir_subcategorias=True,
                apenas_principais=False,
                apenas_personalizadas=False,
                db=db_session,
                current_user=mock_current_user,
            )

            # Assert
            assert result == expected_categorias
            mock_listar.assert_called_once_with(
                db=db_session,
                current_user_id=mock_current_user.id,
                incluir_subcategorias=True,
                apenas_principais=False,
                apenas_personalizadas=False,
            )

    @pytest.mark.asyncio
    async def test_listar_categorias_com_filtros(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve listar categorias aplicando filtros corretamente."""
        # Arrange
        expected_categorias = []

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = expected_categorias

            # Act
            result = await listar_categorias(
                incluir_subcategorias=False,
                apenas_principais=True,
                apenas_personalizadas=True,
                db=db_session,
                current_user=mock_current_user,
            )

            # Assert
            assert result == expected_categorias
            mock_listar.assert_called_once_with(
                db=db_session,
                current_user_id=mock_current_user.id,
                incluir_subcategorias=False,
                apenas_principais=True,
                apenas_personalizadas=True,
            )

    @pytest.mark.asyncio
    async def test_listar_categorias_vazia(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve retornar lista vazia quando não há categorias."""
        # Arrange
        expected_categorias = []

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = expected_categorias

            # Act
            result = await listar_categorias(
                incluir_subcategorias=True,
                apenas_principais=False,
                apenas_personalizadas=False,
                db=db_session,
                current_user=mock_current_user,
            )

            # Assert
            assert result == []
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_obter_categoria_success(
        self,
        db_session: AsyncSession,
        mock_current_user: Usuario,
        sample_categoria_model: Categoria,
    ):
        """Deve obter categoria por ID com sucesso."""
        # Arrange
        categoria_id = 1

        with patch.object(
            CategoriaService, "obter", new_callable=AsyncMock
        ) as mock_obter:
            mock_obter.return_value = sample_categoria_model

            # Act
            result = await obter_categoria(
                db=db_session, categoria_id=categoria_id, current_user=mock_current_user
            )

            # Assert
            assert result == sample_categoria_model
            mock_obter.assert_called_once_with(
                db=db_session,
                categoria_id=categoria_id,
                current_user_id=mock_current_user.id,
            )

    @pytest.mark.asyncio
    async def test_obter_categoria_not_found(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve lançar HTTPException quando categoria não é encontrada."""
        # Arrange
        categoria_id = 999
        expected_error = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada"
        )

        with patch.object(
            CategoriaService, "obter", new_callable=AsyncMock
        ) as mock_obter:
            mock_obter.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await obter_categoria(
                    categoria_id=categoria_id,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == "Categoria não encontrada"

    @pytest.mark.asyncio
    async def test_obter_categoria_acesso_negado(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve lançar HTTPException quando usuário não tem acesso à categoria."""
        # Arrange
        categoria_id = 1
        expected_error = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a esta categoria",
        )

        with patch.object(
            CategoriaService, "obter", new_callable=AsyncMock
        ) as mock_obter:
            mock_obter.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await obter_categoria(
                    categoria_id=categoria_id,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_listar_subcategorias_success(
        self,
        db_session: AsyncSession,
        mock_current_user: Usuario,
        sample_categoria_read: CategoriaRead,
    ):
        """Deve listar subcategorias com sucesso."""
        # Arrange
        categoria_id = 1
        expected_subcategorias = [sample_categoria_read]

        with patch.object(
            CategoriaService, "listar_subcategorias", new_callable=AsyncMock
        ) as mock_listar_sub:
            mock_listar_sub.return_value = expected_subcategorias

            # Act
            result = await listar_subcategorias(
                categoria_id=categoria_id, db=db_session, current_user=mock_current_user
            )

            # Assert
            assert result == expected_subcategorias
            mock_listar_sub.assert_called_once_with(
                db=db_session,
                categoria_id=categoria_id,
                current_user_id=mock_current_user.id,
            )

    @pytest.mark.asyncio
    async def test_listar_subcategorias_categoria_inexistente(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve lançar HTTPException quando categoria pai não existe."""
        # Arrange
        categoria_id = 999
        expected_error = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoria pai não encontrada"
        )

        with patch.object(
            CategoriaService, "listar_subcategorias", new_callable=AsyncMock
        ) as mock_listar_sub:
            mock_listar_sub.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await listar_subcategorias(
                    categoria_id=categoria_id,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_criar_categoria_personalizada_success(
        self,
        db_session: AsyncSession,
        mock_current_user: Usuario,
        sample_categoria_create: CategoriaCreate,
        sample_categoria_model: Categoria,
    ):
        """Deve criar categoria personalizada com sucesso."""
        # Arrange
        with patch.object(
            CategoriaService, "criar", new_callable=AsyncMock
        ) as mock_criar:
            mock_criar.return_value = sample_categoria_model

            # Act
            result = await criar_categoria_personalizada(
                request=sample_categoria_create,
                db=db_session,
                current_user=mock_current_user,
            )

            # Assert
            assert result == sample_categoria_model
            mock_criar.assert_called_once_with(
                db=db_session,
                request=sample_categoria_create,
                current_user_id=mock_current_user.id,
            )

    @pytest.mark.asyncio
    async def test_criar_categoria_nome_duplicado(
        self,
        db_session: AsyncSession,
        mock_current_user: Usuario,
        sample_categoria_create: CategoriaCreate,
    ):
        """Deve lançar HTTPException quando nome da categoria já existe."""
        # Arrange
        expected_error = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma categoria com este nome",
        )

        with patch.object(
            CategoriaService, "criar", new_callable=AsyncMock
        ) as mock_criar:
            mock_criar.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await criar_categoria_personalizada(
                    request=sample_categoria_create,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_atualizar_categoria_success(
        self,
        db_session: AsyncSession,
        mock_current_user: Usuario,
        sample_categoria_create: CategoriaCreate,
        sample_categoria_model: Categoria,
    ):
        """Deve atualizar categoria com sucesso."""
        # Arrange
        categoria_id = 1

        with patch.object(
            CategoriaService, "atualizar", new_callable=AsyncMock
        ) as mock_atualizar:
            mock_atualizar.return_value = sample_categoria_model

            # Act
            result = await atualizar_categoria(
                categoria_id=categoria_id,
                request=sample_categoria_create,
                db=db_session,
                current_user=mock_current_user,
            )

            # Assert
            assert result == sample_categoria_model
            mock_atualizar.assert_called_once_with(
                db=db_session,
                categoria_id=categoria_id,
                request=sample_categoria_create,
                current_user_id=mock_current_user.id,
            )

    @pytest.mark.asyncio
    async def test_atualizar_categoria_nao_personalizada(
        self,
        db_session: AsyncSession,
        mock_current_user: Usuario,
        sample_categoria_create: CategoriaCreate,
    ):
        """Deve lançar HTTPException ao tentar atualizar categoria não personalizada."""
        # Arrange
        categoria_id = 1
        expected_error = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível atualizar categoria padrão do sistema",
        )

        with patch.object(
            CategoriaService, "atualizar", new_callable=AsyncMock
        ) as mock_atualizar:
            mock_atualizar.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await atualizar_categoria(
                    categoria_id=categoria_id,
                    request=sample_categoria_create,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_excluir_categoria_success(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve excluir categoria com sucesso."""
        # Arrange
        categoria_id = 1
        expected_response = {"ok": True}

        with patch.object(
            CategoriaService, "excluir", new_callable=AsyncMock
        ) as mock_excluir:
            mock_excluir.return_value = expected_response

            # Act
            result = await excluir_categoria(
                categoria_id=categoria_id, db=db_session, current_user=mock_current_user
            )

            # Assert
            assert result == expected_response
            mock_excluir.assert_called_once_with(
                db=db_session,
                categoria_id=categoria_id,
                current_user_id=mock_current_user.id,
            )

    @pytest.mark.asyncio
    async def test_excluir_categoria_com_transacoes(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve lançar HTTPException ao tentar excluir categoria com transações."""
        # Arrange
        categoria_id = 1
        expected_error = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir categoria com transações vinculadas",
        )

        with patch.object(
            CategoriaService, "excluir", new_callable=AsyncMock
        ) as mock_excluir:
            mock_excluir.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await excluir_categoria(
                    categoria_id=categoria_id,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_excluir_categoria_nao_personalizada(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve lançar HTTPException ao tentar excluir categoria padrão do sistema."""
        # Arrange
        categoria_id = 1
        expected_error = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível excluir categoria padrão do sistema",
        )

        with patch.object(
            CategoriaService, "excluir", new_callable=AsyncMock
        ) as mock_excluir:
            mock_excluir.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await excluir_categoria(
                    categoria_id=categoria_id,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestCategoriasRouterValidation:
    """Testes de validação e casos de erro."""

    @pytest.mark.asyncio
    async def test_criar_categoria_dados_invalidos(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve lançar HTTPException com dados de entrada inválidos."""
        # Arrange
        invalid_data = CategoriaCreate(
            nome="", descricao="Descrição válida", categoria_pai_id=None
        )
        expected_error = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nome da categoria é obrigatório",
        )

        with patch.object(
            CategoriaService, "criar", new_callable=AsyncMock
        ) as mock_criar:
            mock_criar.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await criar_categoria_personalizada(
                    request=invalid_data, db=db_session, current_user=mock_current_user
                )

            assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_categoria_pai_inexistente(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve lançar HTTPException quando categoria pai não existe."""
        # Arrange
        invalid_data = CategoriaCreate(
            nome="Subcategoria Teste",
            descricao="Descrição válida",
            categoria_pai_id=999,
        )
        expected_error = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoria pai não encontrada"
        )

        with patch.object(
            CategoriaService, "criar", new_callable=AsyncMock
        ) as mock_criar:
            mock_criar.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await criar_categoria_personalizada(
                    request=invalid_data, db=db_session, current_user=mock_current_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestCategoriasRouterExceptions:
    """Testes de tratamento de exceções e casos extremos."""

    @pytest.mark.asyncio
    async def test_listar_categorias_database_error(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve propagar exceção quando ocorre erro no banco de dados."""
        # Arrange
        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.side_effect = Exception("Database connection error")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await listar_categorias(
                    incluir_subcategorias=True,
                    apenas_principais=False,
                    apenas_personalizadas=False,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert str(exc_info.value) == "Database connection error"

    @pytest.mark.asyncio
    async def test_service_timeout(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve propagar exceção quando serviço atinge timeout."""
        # Arrange
        with patch.object(
            CategoriaService, "obter", new_callable=AsyncMock
        ) as mock_obter:
            mock_obter.side_effect = TimeoutError("Service timeout")

            # Act & Assert
            with pytest.raises(asyncio.TimeoutError):
                await obter_categoria(
                    categoria_id=1, db=db_session, current_user=mock_current_user
                )

    @pytest.mark.asyncio
    async def test_categoria_service_indisponivel(
        self, db_session: AsyncSession, mock_current_user: Usuario
    ):
        """Deve propagar exceção quando serviço está indisponível."""
        # Arrange
        expected_error = HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível",
        )

        with patch.object(
            CategoriaService, "listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.side_effect = expected_error

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await listar_categorias(
                    incluir_subcategorias=True,
                    apenas_principais=False,
                    apenas_personalizadas=False,
                    db=db_session,
                    current_user=mock_current_user,
                )

            assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
