from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import categoria
from seeds.categorias_seed import CATEGORIAS_SEED

Categoria = categoria.Categoria


async def seed_categorias(db: AsyncSession) -> None:
    """Popula o banco com as categorias padrão"""
    print("🌱 Iniciando seed de categorias...")

    # Verifica se já existem categorias
    existing = await db.execute(select(Categoria).limit(1))
    if existing.scalars().first():
        print("⚠️  Categorias já existem, seed pulado")
        return
    cat_data: dict[str, Any]
    for cat_data in CATEGORIAS_SEED:
        # Cria categoria principal
        categoria_principal = Categoria(
            nome=cat_data["nome"],
            descricao=cat_data["descricao"],
            cor=cat_data["cor"],
            icone=cat_data["icone"],
            categoria_pai_id=None,
            usuario_id=None,  # Categoria global
        )
        db.add(categoria_principal)
        await db.flush()  # Para obter o ID

        print(f"   ✅ Criada categoria: {cat_data['nome']}")

        # Cria subcategorias
        for subcat_data in cat_data.get("subcategorias", []):
            subcategoria = Categoria(
                nome=subcat_data["nome"],
                descricao=subcat_data["descricao"],
                cor=subcat_data["cor"],
                icone=subcat_data["icone"],
                categoria_pai_id=categoria_principal.id,
                usuario_id=None,
            )
            db.add(subcategoria)
            print(f"      └─ ✅ Criada subcategoria: {subcat_data['nome']}")

    await db.commit()
    print("🎉 Seed de categorias concluído!")
