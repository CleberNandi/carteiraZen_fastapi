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
