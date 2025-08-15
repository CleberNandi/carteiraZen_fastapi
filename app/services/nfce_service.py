from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import nfce
from app.models.nfce import NFCe
from app.schemas.nfce import NotaFiscalCreate


async def criar_nota_fiscal(db: AsyncSession, data: NotaFiscalCreate) -> NFCe:
    return await nfce.create_nota_fiscal(db, data)


async def obter_nota_fiscal(db: AsyncSession, nota_id: int) -> NFCe | None:
    return await nfce.get_nota_fiscal(db, nota_id)


async def listar_notas_fiscais(db: AsyncSession) -> Sequence[NFCe]:
    return await nfce.list_notas_fiscais(db)


async def excluir_nota_fiscal(db: AsyncSession, nota_id: int) -> bool:
    return await nfce.delete_nota_fiscal(db, nota_id)
