# app/services/conta_service.py


from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.conta_corrente import (
    create_conta_corrente,
    delete_conta_corrente,
    get_conta_corrente,
    get_conta_corrente_por_numero,
    get_contas_correntes,
    update_conta_corrente,
)
from app.schemas.conta_corrente import ContaCreate, ContaOut, ContaUpdate


class ContaService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, skip: int = 0, limit: int = 100) -> list[ContaOut]:
        contas = get_contas_correntes(self.db, skip=skip, limit=limit)
        return [ContaOut.model_validate(c) for c in contas]

    def obter(self, conta_id: int) -> ContaOut:
        conta = get_conta_corrente(self.db, conta_id)
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        return ContaOut.model_validate(conta)

    def criar(self, conta: ContaCreate, user_id: int) -> ContaOut:
        existente = get_conta_corrente_por_numero(
            self.db, agencia_id=conta.agencia_id, numero=conta.numero
        )
        if existente:
            raise HTTPException(
                status_code=400, detail="Conta já cadastrada para essa agência"
            )

        if conta.saldo_inicial < 0:
            raise HTTPException(
                status_code=400, detail="Saldo inicial não pode ser negativo"
            )

        conta_result = create_conta_corrente(self.db, conta, user_id)
        return ContaOut.model_validate(conta_result)

    def atualizar(
        self, conta_id: int, conta_data: ContaUpdate, executor_id: int
    ) -> ContaOut | None:
        conta = get_conta_corrente(self.db, conta_id)
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada.")

        if conta_data.saldo_inicial < 0:
            raise HTTPException(status_code=400, detail="Saldo não pode ser negativo.")

        if conta_data.numero != conta.numero:
            raise HTTPException(
                status_code=400, detail="Não é permitido alterar o número da conta."
            )

        if conta_data.agencia_id != conta.agencia_id:
            raise HTTPException(
                status_code=400, detail="Não é permitido alterar a agência da conta."
            )

        conta_update = update_conta_corrente(self.db, conta, conta_data, executor_id)
        return ContaOut.model_validate(conta_update) if conta_update else None

    def deletar(self, conta_id: int, executor_id: int) -> None:
        conta = get_conta_corrente(self.db, conta_id)
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada.")

        delete_conta_corrente(self.db, conta, executor_id)
