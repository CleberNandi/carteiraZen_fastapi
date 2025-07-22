from sqlalchemy.orm import Session

from app import crud
from app.schemas.fatura import FaturaCreate, FaturaRead, FaturaUpdate


class FaturaService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self) -> list[FaturaRead]:
        faturas = crud.fatura.get_faturas(self.db)
        return [FaturaRead.model_validate(f) for f in faturas]

    def buscar_por_id(self, fatura_id: int) -> FaturaRead | None:
        fatura = crud.fatura.get_fatura(self.db, fatura_id)
        if not fatura:
            return None
        return FaturaRead.model_validate(fatura)

    def validar_unicidade(self, cartao_id: int, mes: int, ano: int) -> bool:
        return crud.fatura.validar_unicidade(self.db, cartao_id, mes, ano) is not None

    def criar(self, fatura: FaturaCreate, executor_id: int) -> FaturaRead:
        nova_fatura = crud.fatura.create_fatura(self.db, fatura, executor_id)
        return FaturaRead.model_validate(nova_fatura)

    def atualizar(
        self, fatura_id: int, fatura_update: FaturaUpdate, executor_id: int
    ) -> FaturaRead | None:
        fatura_atualizada = crud.fatura.update_fatura(
            self.db, fatura_id, fatura_update, executor_id
        )
        if not fatura_atualizada:
            return None
        return FaturaRead.model_validate(fatura_atualizada)

    def remover(self, fatura_id: int, executor_id: int) -> bool:
        return crud.fatura.delete_fatura(self.db, fatura_id, executor_id)
