# app/services/conta_service.py


from crud.conta import (
    create_conta,
    delete_conta,
    get_conta,
    get_conta_por_numero,
    get_contas,
    update_conta,
)
from fastapi import HTTPException
from schemas.conta import ContaCreate, ContaOut, ContaUpdate
from sqlalchemy.orm import Session


class ContaService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, skip: int = 0, limit: int = 100) -> list[ContaOut]:
        contas = get_contas(self.db, skip=skip, limit=limit)
        return [ContaOut.model_validate(c) for c in contas]

    def obter(self, conta_id: int) -> ContaOut:
        conta = get_conta(self.db, conta_id)
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        return ContaOut.model_validate(conta)

    def criar(self, conta: ContaCreate, user_id: int) -> ContaOut:
        existente = get_conta_por_numero(self.db, numero=conta.numero)
        if existente:
            raise HTTPException(
                status_code=400, detail="Conta já cadastrada para essa agência"
            )

        if conta.saldo_inicial < 0:
            raise HTTPException(
                status_code=400, detail="Saldo inicial não pode ser negativo"
            )

        conta_result = create_conta(self.db, conta, user_id)
        return ContaOut.model_validate(conta_result)

    def atualizar(
        self, conta_id: int, conta_data: ContaUpdate, executor_id: int
    ) -> ContaOut | None:
        conta = get_conta(self.db, conta_id)
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada.")

        if conta_data.saldo_inicial < 0:
            raise HTTPException(status_code=400, detail="Saldo não pode ser negativo.")

        if conta_data.numero != conta.numero:
            raise HTTPException(
                status_code=400, detail="Não é permitido alterar o número da conta."
            )

        conta_update = update_conta(self.db, conta, conta_data, executor_id)
        return ContaOut.model_validate(conta_update) if conta_update else None

    def deletar(self, conta_id: int, executor_id: int) -> None:
        conta = get_conta(self.db, conta_id)
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada.")

        delete_conta(self.db, conta, executor_id)
