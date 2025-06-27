from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app

client = TestClient(app)

# Cria as tabelas no SQLite em memória antes dos testes
Base.metadata.create_all(bind=engine)


def test_root():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!"}


def test_create_user():
    # Limpa a tabela antes do teste
    with engine.begin() as conn:
        conn.execute(Base.metadata.tables["users"].delete())
    data = {"name": "Alice", "email": "alice@example.com"}
    response = client.post("/api/v1/users/?user_id=1", json=data)
    if response.status_code != 200:
        print("Erro ao criar usuário:", response.status_code, response.text)
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"
    assert response.json()["email"] == "alice@example.com"
    assert "id" in response.json()


def test_get_users():
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_by_id():
    # Cria usuário para garantir existência
    data = {"name": "Bob", "email": "bob@example.com"}
    create_resp = client.post("/api/v1/users/?user_id=1", json=data)
    user_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_user_by_email():
    email = "carol@example.com"
    data = {"name": "Carol", "email": email}
    client.post("/api/v1/users/?user_id=1", json=data)
    response = client.get(f"/api/v1/users/by-email/{email}")
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_create_user_duplicate_email():
    data = {"name": "Dave", "email": "dave@example.com"}
    client.post("/api/v1/users/?user_id=1", json=data)
    response = client.post("/api/v1/users/?user_id=1", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
