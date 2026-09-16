# Adicione estas fixtures ao seu arquivo conftest.py

import pytest

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaRead


@pytest.fixture
def sample_categoria_read():
    """Fixture para CategoriaRead de exemplo."""
    return CategoriaRead(
        id=1,
        nome="Alimentação",
        descricao="Categoria para gastos com alimentação",
        icone="food",
        categoria_pai_id=None,
        cor="#FF5733",
    )


@pytest.fixture
def sample_categoria_create():
    """Fixture para CategoriaCreate de exemplo."""
    return CategoriaCreate(
        nome="Alimentação",
        cor="#FF5733",
        icone="food",
        descricao="Categoria para gastos com alimentação",
        categoria_pai_id=None,
    )


@pytest.fixture
def sample_categoria_model():
    """Fixture para modelo Categoria de exemplo."""
    return Categoria(
        id=1,
        nome="Alimentação",
        cor="#FF5733",
        icone="food",
        descricao="Categoria para gastos com alimentação",
        categoria_pai_id=None,
    )
