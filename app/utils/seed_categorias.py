from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from seeds.categorias_seed import CATEGORIAS_SEED


def seed_categorias(db: Session) -> None:
    """Popula o banco com as categorias padrão"""
    from models.categoria import Categoria

    print("🌱 Iniciando seed de categorias...")

    for cat_data in CATEGORIAS_SEED:
        # Verifica se categoria principal já existe
        cat_data: dict[str, Any]
        categoria_existente = (
            db.query(Categoria)
            .filter(
                and_(
                    Categoria.nome == cat_data["nome"],
                    Categoria.categoria_pai_id.is_(None),
                    Categoria.usuario_id.is_(None),
                )
            )
            .first()
        )

        if categoria_existente:
            print(f"   ⚠️  Categoria '{cat_data['nome']}' já existe, pulando...")
            continue

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
        db.flush()  # Para obter o ID

        print(f"   ✅ Criada categoria: {cat_data['nome']}")

        # Cria subcategorias
        for subcat_data in cat_data.get("subcategorias", []):
            subcategoria = Categoria(
                nome=subcat_data["nome"],
                descricao=subcat_data["descricao"],
                cor=subcat_data["cor"],
                icone=subcat_data["icone"],
                categoria_pai_id=categoria_principal.id,
                usuario_id=None,  # Categoria global
            )

            db.add(subcategoria)
            print(f"      └─ ✅ Criada subcategoria: {subcat_data['nome']}")

    db.commit()
    print("🎉 Seed de categorias concluído!")
