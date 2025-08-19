from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import categoria, transacao, usuario
from app.schemas.categoria import CategoriaCreate, CategoriaRead

Categoria = categoria.Categoria
Usuario = usuario.Usuario
Transacao = transacao.Transacao


class CategoriaService:
    @staticmethod
    async def listar(
        db: AsyncSession,
        current_user: Usuario,
        *,
        incluir_subcategorias: bool = True,
        apenas_principais: bool = False,
        apenas_personalizadas: bool = False,
    ) -> list[CategoriaRead]:
        stmt = select(Categoria).where(Categoria.ativo.is_(True))

        if apenas_personalizadas:
            stmt = stmt.where(Categoria.usuario_id == current_user.id)
        else:
            stmt = stmt.where(
                or_(
                    Categoria.usuario_id == current_user.id,
                    Categoria.usuario_id.is_(None),
                )
            )

        if apenas_principais or not incluir_subcategorias:
            stmt = stmt.where(Categoria.categoria_pai_id.is_(None))

        stmt = stmt.order_by(Categoria.nome)
        result = await db.execute(stmt)
        categorias = result.scalars().all()

        return [CategoriaRead.model_validate(cat) for cat in categorias]

    @staticmethod
    async def obter(
        db: AsyncSession,
        current_user: Usuario,
        categoria_id: int,
    ) -> Categoria:
        stmt = select(Categoria).where(
            Categoria.id == categoria_id,
            Categoria.ativo.is_(True),
            or_(
                Categoria.usuario_id == current_user.id, Categoria.usuario_id.is_(None)
            ),
        )
        result = await db.execute(stmt)
        categoria = result.scalars().first()

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada"
            )

        return categoria

    @staticmethod
    async def listar_subcategorias(
        db: AsyncSession,
        current_user: Usuario,
        categoria_id: int,
    ) -> list[CategoriaRead]:
        # Verifica se categoria pai existe
        categoria_pai = await CategoriaService.obter(db, current_user, categoria_id)

        stmt = (
            select(Categoria)
            .where(
                Categoria.categoria_pai_id == categoria_pai.id,
                Categoria.ativo.is_(True),
                or_(
                    Categoria.usuario_id == current_user.id,
                    Categoria.usuario_id.is_(None),
                ),
            )
            .order_by(Categoria.nome)
        )
        result = await db.execute(stmt)
        subcategorias = result.scalars().all()

        return [CategoriaRead.model_validate(cat) for cat in subcategorias]

    @staticmethod
    async def criar(
        db: AsyncSession,
        current_user: Usuario,
        request: CategoriaCreate,
    ) -> Categoria:
        categoria = Categoria(
            nome=request.nome,
            descricao=request.descricao,
            cor=request.cor,
            icone=request.icone,
            categoria_pai_id=request.categoria_pai_id,
            usuario_id=current_user.id,
        )
        db.add(categoria)
        await db.commit()
        await db.refresh(categoria)
        return categoria

    @staticmethod
    async def atualizar(
        db: AsyncSession,
        current_user: Usuario,
        categoria_id: int,
        request: CategoriaCreate,
    ) -> Categoria:
        categoria = await CategoriaService.obter(db, current_user, categoria_id)

        # Valida se já existem transações vinculadas
        stmt = select(Transacao).where(Transacao.categoria_id == categoria.id)
        result = await db.execute(stmt)
        transacoes = result.scalars().first()

        if transacoes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria não pode ser alterada pois já está vinculada a transações",
            )

        # Atualiza campos permitidos
        categoria.nome = request.nome
        categoria.descricao = request.descricao
        categoria.cor = request.cor
        categoria.icone = request.icone
        categoria.categoria_pai_id = request.categoria_pai_id

        db.add(categoria)
        await db.commit()
        await db.refresh(categoria)

        return categoria
