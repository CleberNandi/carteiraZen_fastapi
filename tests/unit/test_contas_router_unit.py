from unittest.mock import AsyncMock, patch

from fastapi import status
from httpx import AsyncClient
import pytest

from app.schemas.conta import ContaListResponse, ContaRead, ContaResumo, TipoConta


class TestContasRouterUnit:
    """Testes unitários para o router de contas"""

    @pytest.fixture
    def mock_conta_read(self):
        """Fixture para ContaRead mock"""
        return ContaRead(
            id=1,
            nome="Conta Corrente",
            tipo=TipoConta.CORRENTE,
            saldo_cents=50000,  # R$ 500,00
            cheque_especial_cents=100000,  # R$ 1000,00
            cor="#FF5733",
            incluir_na_soma_inicial=True,
            conta_padrao=True,
            banco_id=None,
        )

    @pytest.fixture
    def mock_conta_list_response(self):
        """Fixture para ContaListResponse mock"""
        conta_resumo = ContaResumo(
            id=1,
            nome="Conta Corrente",
            tipo="CORRENTE",  # type: ignore
            saldo_decimal=500.00,
            cor="#FF5733",
            ativo=True,
            conta_padrao=True,
        )
        return ContaListResponse(contas=[conta_resumo], total=1, saldo_total=500.00)

    @pytest.mark.asyncio
    async def test_criar_conta_success(
        self,
        client: AsyncClient,
        authenticated_user: dict[str, str],
        mock_conta_read: ContaRead,
    ):
        """Testa criação de conta com sucesso"""
        conta_data = {
            "nome": "Conta Corrente",
            "tipo": "CORRENTE",
            "saldo_cents": 50000,
            "cheque_especial_cents": 100000,
            "cor": "#FF5733",
            "incluir_na_soma_inicial": True,
            "conta_padrao": True,
        }

        with patch(
            "app.services.conta_service.ContaService.criar", new_callable=AsyncMock
        ) as mock_criar:
            mock_criar.return_value = mock_conta_read

            response = await client.post(
                "/api/v1/contas/", json=conta_data, headers=authenticated_user
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()

            assert data["nome"] == "Conta Corrente"
            assert data["tipo"] == "CORRENTE"
            assert data["saldo_decimal"] == 500.00
            assert data["conta_padrao"] is True

            # Verifica se o service foi chamado
            mock_criar.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_conta_nome_duplicado(
        self, client: AsyncClient, authenticated_user: dict[str, str]
    ):
        """Testa erro ao criar conta com nome duplicado"""
        conta_data = {"nome": "Conta Existente", "tipo": "CORRENTE", "cor": "#FF5733"}

        from fastapi import HTTPException

        with patch(
            "app.services.conta_service.ContaService.criar", new_callable=AsyncMock
        ) as mock_criar:
            mock_criar.side_effect = HTTPException(
                status_code=400, detail="Já existe uma conta com este nome"
            )

            response = await client.post(
                "/api/v1/contas/", json=conta_data, headers=authenticated_user
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Já existe uma conta com este nome" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_listar_contas_success(
        self,
        client: AsyncClient,
        authenticated_user: dict[str, str],
        mock_conta_list_response: ContaListResponse,
    ):
        """Testa listagem de contas com sucesso"""
        with patch(
            "app.services.conta_service.ContaService.listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = mock_conta_list_response

            response = await client.get("/api/v1/contas/", headers=authenticated_user)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["total"] == 1
            assert data["saldo_total"] == 500.00
            assert len(data["contas"]) == 1
            assert data["contas"][0]["nome"] == "Conta Corrente"

            # Verifica parâmetros padrão
            mock_listar.assert_called_once()
            call_args = mock_listar.call_args
            assert call_args.kwargs["skip"] == 0
            assert call_args.kwargs["limit"] == 100
            assert call_args.kwargs["incluir_inativas"] is False

    @pytest.mark.asyncio
    async def test_listar_contas_com_filtros(
        self,
        client: AsyncClient,
        authenticated_user: dict[str, str],
        mock_conta_list_response: ContaListResponse,
    ):
        """Testa listagem com filtros aplicados"""
        with patch(
            "app.services.conta_service.ContaService.listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = mock_conta_list_response

            response = await client.get(
                "/api/v1/contas/?skip=10&limit=50&tipo=CORRENTE&incluir_inativas=true",
                headers=authenticated_user,
            )

            assert response.status_code == status.HTTP_200_OK

            # Verifica se os filtros foram passados
            call_args = mock_listar.call_args
            assert call_args.kwargs["skip"] == 10
            assert call_args.kwargs["limit"] == 50
            assert call_args.kwargs["incluir_inativas"] is True

    @pytest.mark.asyncio
    async def test_buscar_conta_success(
        self,
        client: AsyncClient,
        authenticated_user: dict[str, str],
        mock_conta_read: ContaRead,
    ):
        """Testa busca de conta por ID com sucesso"""
        with patch(
            "app.services.conta_service.ContaService.buscar_por_id",
            new_callable=AsyncMock,
        ) as mock_buscar:
            mock_buscar.return_value = mock_conta_read

            response = await client.get("/api/v1/contas/1", headers=authenticated_user)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["id"] == 1
            assert data["nome"] == "Conta Corrente"

            # Verifica se foi chamado com ID correto - FIXED
            mock_buscar.assert_called_once()
            call_args = mock_buscar.call_args
            # Use args[0] para o primeiro argumento posicional ou kwargs para argumentos nomeados
            assert call_args.args[1] == 1  # conta_id (segundo argumento posicional)

    @pytest.mark.asyncio
    async def test_buscar_conta_nao_encontrada(
        self, client: AsyncClient, authenticated_user: dict[str, str]
    ):
        """Testa erro ao buscar conta inexistente"""
        from fastapi import HTTPException

        with patch(
            "app.services.conta_service.ContaService.buscar_por_id",
            new_callable=AsyncMock,
        ) as mock_buscar:
            mock_buscar.side_effect = HTTPException(
                status_code=404, detail="Conta não encontrada"
            )

            response = await client.get(
                "/api/v1/contas/999", headers=authenticated_user
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Conta não encontrada" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_atualizar_conta_success(
        self,
        client: AsyncClient,
        authenticated_user: dict[str, str],
        mock_conta_read: ContaRead,
    ):
        """Testa atualização de conta com sucesso"""
        update_data = {"nome": "Conta Corrente Atualizada", "cor": "#00FF00"}

        # Atualiza o mock para refletir os dados atualizados
        mock_conta_read.nome = "Conta Corrente Atualizada"
        mock_conta_read.cor = "#00FF00"

        with patch(
            "app.services.conta_service.ContaService.atualizar", new_callable=AsyncMock
        ) as mock_atualizar:
            mock_atualizar.return_value = mock_conta_read

            response = await client.put(
                "/api/v1/contas/1", json=update_data, headers=authenticated_user
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["nome"] == "Conta Corrente Atualizada"
            assert data["cor"] == "#00FF00"

            # Verifica parâmetros da chamada - FIXED
            mock_atualizar.assert_called_once()
            call_args = mock_atualizar.call_args
            assert call_args.args[1] == 1  # conta_id

    @pytest.mark.asyncio
    async def test_excluir_conta_success(
        self, client: AsyncClient, authenticated_user: dict[str, str]
    ):
        """Testa exclusão de conta com sucesso"""
        with patch(
            "app.services.conta_service.ContaService.excluir", new_callable=AsyncMock
        ) as mock_excluir:
            mock_excluir.return_value = {"ok": True}

            response = await client.delete(
                "/api/v1/contas/1", headers=authenticated_user
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["ok"] is True

            # Verifica se foi chamado com ID correto - FIXED
            mock_excluir.assert_called_once()
            call_args = mock_excluir.call_args
            assert call_args.args[1] == 1  # conta_id

    @pytest.mark.asyncio
    async def test_excluir_conta_com_transacoes(
        self, client: AsyncClient, authenticated_user: dict[str, str]
    ):
        """Testa erro ao excluir conta com transações"""
        from fastapi import HTTPException

        with patch(
            "app.services.conta_service.ContaService.excluir", new_callable=AsyncMock
        ) as mock_excluir:
            mock_excluir.side_effect = HTTPException(
                status_code=400,
                detail="Não é possível excluir a conta, existem transações vinculadas",
            )

            response = await client.delete(
                "/api/v1/contas/1", headers=authenticated_user
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "transações vinculadas" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_definir_conta_padrao_success(
        self,
        client: AsyncClient,
        authenticated_user: dict[str, str],
        mock_conta_read: ContaRead,
    ):
        """Testa definir conta como padrão com sucesso"""
        with patch(
            "app.services.conta_service.ContaService.definir_como_padrao",
            new_callable=AsyncMock,
        ) as mock_definir:
            mock_definir.return_value = mock_conta_read

            response = await client.patch(
                "/api/v1/contas/1/definir-padrao", headers=authenticated_user
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["conta_padrao"] is True

            # Verifica se foi chamado com ID correto - FIXED
            mock_definir.assert_called_once()
            call_args = mock_definir.call_args
            assert call_args.args[1] == 1  # conta_id

    @pytest.mark.asyncio
    async def test_definir_conta_padrao_ja_eh_padrao(
        self, client: AsyncClient, authenticated_user: dict[str, str]
    ):
        """Testa erro ao definir conta que já é padrão"""
        from fastapi import HTTPException

        with patch(
            "app.services.conta_service.ContaService.definir_como_padrao",
            new_callable=AsyncMock,
        ) as mock_definir:
            mock_definir.side_effect = HTTPException(
                status_code=400, detail="Esta conta já é a conta padrão"
            )

            response = await client.patch(
                "/api/v1/contas/1/definir-padrao", headers=authenticated_user
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "já é a conta padrão" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_query_params_validation(
        self,
        client: AsyncClient,
        authenticated_user: dict[str, str],
        mock_conta_list_response: ContaListResponse,
    ):
        """Testa validação de parâmetros de query"""
        with patch(
            "app.services.conta_service.ContaService.listar", new_callable=AsyncMock
        ) as mock_listar:
            mock_listar.return_value = mock_conta_list_response

            # Teste com parâmetros inválidos (skip negativo)
            response = await client.get(
                "/api/v1/contas/?skip=-1", headers=authenticated_user
            )

            # FastAPI deve retornar erro de validação
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

            # Teste com limit muito alto
            response = await client.get(
                "/api/v1/contas/?limit=2000", headers=authenticated_user
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_path_params_validation(
        self, client: AsyncClient, authenticated_user: dict[str, str]
    ):
        """Testa validação de parâmetros de path"""
        # ID inválido (não numérico)
        response = await client.get("/api/v1/contas/abc", headers=authenticated_user)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
