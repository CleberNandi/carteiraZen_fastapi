from typing import TYPE_CHECKING, Optional

from mixins.sync_mixins import SyncMixin
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.mixins.mixins import Mixins

if TYPE_CHECKING:
    from models.orcamento import Orcamento
    from models.sub_categoria import SubCategoria
    from models.transacao import Transacao
    from models.usuario import Usuario


class Categoria(Base, Mixins, SyncMixin):
    __tablename__ = "categorias"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    cor: Mapped[str | None] = mapped_column(String(7))  # Hex color
    icone: Mapped[str | None] = mapped_column(String(50))  # Icon name
    categoria_pai_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"))
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id")
    )  # NULL = categoria global

    # Relacionamentos
    categoria_pai: Mapped[Optional["Categoria"]] = relationship(
        "Categoria",
        remote_side="Categoria.id",
        back_populates="subcategorias_categorias",
    )
    subcategorias_categorias: Mapped[list["Categoria"]] = relationship(
        "Categoria", back_populates="categoria_pai"
    )
    sub_categorias: Mapped[list["SubCategoria"]] = relationship(
        "SubCategoria", back_populates="categoria"
    )
    usuario: Mapped[Optional["Usuario"]] = relationship(back_populates="categorias")
    transacoes: Mapped[list["Transacao"]] = relationship(back_populates="categoria")
    orcamentos: Mapped[list["Orcamento"]] = relationship(back_populates="categoria")

    @property
    def nome_completo(self) -> str:
        """Retorna o nome completo da categoria (Pai > Filha)"""
        if self.categoria_pai:
            return f"{self.categoria_pai.nome} > {self.nome}"
        return self.nome

    @property
    def eh_subcategoria(self) -> bool:
        """Verifica se é uma subcategoria"""
        return self.categoria_pai_id is not None
