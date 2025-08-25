from datetime import UTC, date, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

from fastapi import status
from httpx import AsyncClient
from jose import jwt
import pytest

from app.core.config import settings
from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.main import app
from app.schemas.fatura import FaturaResponse

# ---------------------------
# HELPERS / FIXTURES REUTILIZÁVEIS
# ---------------------------


def create_mock_db(all_return: list[Any] | None = None) -> MagicMock:
    """Cria um mock de DB com query encadeada padrão"""
    all_return = all_return or []
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = all_return
    mock_db.query.return_value = mock_query
    return mock_db


def create_mock_fatura_obj(fatura: FaturaResponse) -> MagicMock:
    """Cria um mock de objeto Fatura a partir de um FaturaResponse"""
    return MagicMock(**fatura.model_dump())


def override_dependencies(client: AsyncClient, user: MagicMock, db: MagicMock):
    """Override das dependências do FastAPI"""
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_async_db] = lambda: db
    return app.dependency_overrides


class TestFaturaRouterUnit:
    @pytest.fixture
    def mock_user_data(self) -> dict[str, Any]:
        return {
            "id": 1,
            "email": "test1@example.com",
            "nome": "Test User",
            "is_verified": True,
        }

    @pytest.fixture
    def mock_user_object(self, mock_user_data: dict[str, Any]) -> MagicMock:
        user_mock = MagicMock()
        user_mock.id = mock_user_data["id"]
        user_mock.email = mock_user_data["email"]
        user_mock.nome = mock_user_data["nome"]
        user_mock.is_verified = mock_user_data["is_verified"]
        return user_mock

    @pytest.fixture
    def access_token(self, mock_user_data: dict[str, Any]) -> str:
        SECRET_KEY: str = settings.SECRET_KEY  # noqa: N806
        ALGORITHM: str = "HS256"  # noqa: N806
        to_encode: dict[str, Any] = {
            "sub": str(mock_user_data["id"]),
            "email": mock_user_data["email"],
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @pytest.fixture
    def auth_headers(self, access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}

    @pytest.fixture
    def mock_fatura_response(self) -> FaturaResponse:
        return FaturaResponse(
            id=1,
            cartao_id=1,
            usuario_id=1,
            data_fechamento=date.today(),
            data_vencimento=date.today(),
            data_inicio_periodo=date.today(),
            data_fim_periodo=date.today(),
            valor_total=1000,
            valor_pago=200,
            valor_minimo=100,
            paga=False,
            vencida=False,
            juros_mora=None,
            multa=None,
            observacoes=None,
            saldo_devedor=800,
            percentual_pago=20.0,
            dias_vencimento=10,
        )

    # ---------------------------
    # TESTES
    # ---------------------------

    @pytest.mark.asyncio
    async def test_listar_faturas_success(
        self,
        client: AsyncClient,
        mock_user_object: MagicMock,
        auth_headers: dict[str, str],
    ) -> None:
        mock_db = create_mock_db(all_return=[])
        override_dependencies(client, mock_user_object, mock_db)

        try:
            response = await client.get("/api/v1/faturas/", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_obter_fatura_success(
        self,
        client: AsyncClient,
        mock_user_object: MagicMock,
        mock_fatura_response: FaturaResponse,
        auth_headers: dict[str, str],
    ) -> None:
        mock_fatura_obj = create_mock_fatura_obj(mock_fatura_response)
        mock_db = create_mock_db(all_return=[mock_fatura_obj])
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_fatura_obj
        )
        override_dependencies(client, mock_user_object, mock_db)

        try:
            response = await client.get(
                f"/api/v1/faturas/{mock_fatura_response.id}", headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            data: dict[str, Any] = response.json()
            assert data["id"] == mock_fatura_response.id
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_listar_faturas_vazia(
        self,
        client: AsyncClient,
        mock_user_object: MagicMock,
        auth_headers: dict[str, str],
    ) -> None:
        mock_db = create_mock_db(all_return=[])
        override_dependencies(client, mock_user_object, mock_db)

        try:
            response = await client.get("/api/v1/faturas/", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []
        finally:
            app.dependency_overrides.clear()
