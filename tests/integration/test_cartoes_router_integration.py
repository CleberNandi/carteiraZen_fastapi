from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
import pytest
from schemas.cartao import CartaoCreate


@pytest.mark.asyncio
async def test_create_cartao_integration(
    client: AsyncClient,
    make_fake_cartao_create: CartaoCreate,
    authenticated_user: dict[str, str],
):
    payload = jsonable_encoder(make_fake_cartao_create)
    response = await client.post(
        "/api/v1/cartoes/", json=payload, headers=authenticated_user
    )
    assert response.status_code == 200
    data = response.json()
    assert data["descricao"] == "Cartão de Teste"
    assert "id" in data


# async def test_get_cartao_integration(async_client: AsyncClient):
#     payload = build_cartao_payload()
#     create_resp = await async_client.post("/api/v1/cartoes/", json=payload)
#     cartao_id = create_resp.json()["id"]

#     response = await async_client.get(f"/api/v1/cartoes/{cartao_id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == cartao_id
#     assert data["bandeira"] == "Visa"


# async def test_list_cartoes_integration(async_client: AsyncClient):
#     response = await async_client.get("/api/v1/cartoes/")
#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)


# async def test_update_cartao_integration(async_client: AsyncClient):
#     payload = build_cartao_payload()
#     create_resp = await async_client.post("/api/v1/cartoes/", json=payload)
#     cartao_id = create_resp.json()["id"]

#     updated_payload = payload.copy()
#     updated_payload["descricao"] = "Cartão Atualizado"

#     response = await async_client.put(f"/api/v1/cartoes/{cartao_id}", json=updated_payload)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["descricao"] == "Cartão Atualizado"


# async def test_delete_cartao_integration(async_client: AsyncClient):
#     payload = build_cartao_payload()
#     create_resp = await async_client.post("/api/v1/cartoes/", json=payload)
#     cartao_id = create_resp.json()["id"]

#     response = await async_client.delete(f"/api/v1/cartoes/{cartao_id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert data == {"ok": True}


# async def test_get_cartao_not_found_integration(async_client: AsyncClient):
#     response = await async_client.get("/api/v1/cartoes/99999")
#     assert response.status_code == 404


# async def test_update_cartao_not_found_integration(async_client: AsyncClient):
#     payload = build_cartao_payload()
#     response = await async_client.put("/api/v1/cartoes/99999", json=payload)
#     assert response.status_code == 404


# async def test_delete_cartao_not_found_integration(async_client: AsyncClient):
#     response = await async_client.delete("/api/v1/cartoes/99999")
#     assert response.status_code == 404
