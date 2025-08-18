from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import categoria, usuario
from app.schemas.categoria import CategoriaRead

Categoria = categoria.Categoria
Usuario = usuario.Usuario

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("/", response_model=list[CategoriaRead])
def listar_categorias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    *,
    incluir_subcategorias: bool = True,
    apenas_principais: bool = False,
    apenas_personalizadas: bool = False,
) -> list[CategoriaRead]:
    """Lista as categorias disponíveis"""
    query = db.query(Categoria).filter(Categoria.ativo.is_(True))

    if apenas_personalizadas:
        query = query.filter(Categoria.usuario_id == current_user.id)
    else:
        # Inclui categorias globais e personalizadas do usuário
        query = query.filter(
            (Categoria.usuario_id == current_user.id) | (Categoria.usuario_id.is_(None))
        )

    if apenas_principais or not incluir_subcategorias:
        query = query.filter(Categoria.categoria_pai_id.is_(None))

    categorias = query.order_by(Categoria.nome).all()

    return [CategoriaRead.model_validate(cat) for cat in categorias]


@router.get("/{categoria_id}", response_model=CategoriaRead)
def obter_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> Categoria:
    """Obtém detalhes de uma categoria específica"""
    categoria = (
        db.query(Categoria)
        .filter(
            Categoria.id == categoria_id,
            Categoria.ativo.is_(True),
            (
                (Categoria.usuario_id == current_user.id)
                | (Categoria.usuario_id.is_(None))
            ),
        )
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada"
        )

    return categoria


@router.get("/{categoria_id}/subcategorias", response_model=CategoriaRead)
def listar_subcategorias(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[Categoria]:
    """Lista as subcategorias de uma categoria"""
    # Verifica se categoria pai existe
    categoria_pai = (
        db.query(Categoria)
        .filter(
            Categoria.id == categoria_id,
            Categoria.ativo.is_(True),
            (
                (Categoria.usuario_id == current_user.id)
                | (Categoria.usuario_id.is_(None))
            ),
        )
        .first()
    )

    if not categoria_pai:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada"
        )

    return (
        db.query(Categoria)
        .filter(
            Categoria.categoria_pai_id == categoria_id,
            Categoria.ativo.is_(True),
            (
                (Categoria.usuario_id == current_user.id)
                | (Categoria.usuario_id.is_(None))
            ),
        )
        .order_by(Categoria.nome)
        .all()
    )


@router.post("/", response_model=CategoriaRead)
def criar_categoria_personalizada(
    categoria_data: dict[str, str],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> Categoria:
    """Cria uma categoria personalizada para o usuário"""
    categoria = Categoria(
        nome=categoria_data["nome"],
        descricao=categoria_data.get("descricao"),
        cor=categoria_data.get("cor"),
        icone=categoria_data.get("icone"),
        categoria_pai_id=categoria_data.get("categoria_pai_id"),
        usuario_id=current_user.id,
    )

    db.add(categoria)
    db.commit()
    db.refresh(categoria)

    return categoria
