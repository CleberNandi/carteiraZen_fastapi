from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nfce import NFCe
from app.models.nfce_itens import NFCeItens
from app.schemas.nfce import NotaFiscalCreate


async def create_nota_fiscal(db: AsyncSession, obj_in: NotaFiscalCreate) -> NFCe:
    nota_fiscal = NFCe(
        emitente=obj_in.emitente,
        cnpj=obj_in.cnpj,
        endereco=obj_in.endereco,
        valor_total=obj_in.valor_total,
        numero=obj_in.numero,
        serie=obj_in.serie,
        data_emissao=obj_in.data_emissao,
        protocolo=obj_in.protocolo,
        chave_acesso=obj_in.chave_acesso,
        consumidor=obj_in.consumidor,
        tributos=obj_in.tributos,
    )

    for item_in in obj_in.itens:
        item = NFCeItens(
            descricao=item_in.descricao,
            quantidade=item_in.quantidade,
            unidade=item_in.unidade,
            valor_unitario=item_in.valor_unitario,
            valor_total=item_in.valor_total,
        )
        nota_fiscal.itens.append(item)

    db.add(nota_fiscal)
    await db.commit()
    await db.refresh(nota_fiscal)
    return nota_fiscal


async def get_nota_fiscal(db: AsyncSession, nota_id: int) -> NFCe | None:
    result = await db.execute(select(NFCe).where(NFCe.id == nota_id).options())
    return result.scalar_one_or_none()


async def list_notas_fiscais(db: AsyncSession) -> Sequence[NFCe]:
    result = await db.execute(select(NFCe))
    return result.scalars().all()


async def delete_nota_fiscal(db: AsyncSession, nota_id: int) -> bool:
    nota = await get_nota_fiscal(db, nota_id)
    if not nota:
        return False
    await db.delete(nota)
    await db.commit()
    return True
