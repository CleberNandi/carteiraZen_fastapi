# app/services/transacoes.py


from sqlalchemy.orm import Session

from app.crud.transacao import (
    create_transacao,
    delete_transacao_by_user,
    get_transacao_by_id_and_user,
    listar_transacoes_por_usuario,
    update_transacao_by_user,
)
from app.schemas.transacao import TransacaoCreate, TransacaoRead, TransacaoUpdate


class TransacaoService:
    def __init__(self, db: Session, user_id: int) -> None:
        self.db = db
        self.user_id = user_id

    def criar(self, transacao: TransacaoCreate) -> TransacaoRead:
        nova = create_transacao(self.db, transacao)
        return TransacaoRead.model_validate(nova)

    def listar(self) -> list[TransacaoRead]:
        transacoes = listar_transacoes_por_usuario(self.db, self.user_id)
        return [TransacaoRead.model_validate(t) for t in transacoes]

    def buscar_por_id(self, transacao_id: int) -> TransacaoRead | None:
        transacao = get_transacao_by_id_and_user(self.db, transacao_id, self.user_id)
        if not transacao:
            return None
        return TransacaoRead.model_validate(transacao)

    def atualizar(
        self, transacao_id: int, transacao_in: TransacaoUpdate
    ) -> TransacaoRead | None:
        atualizada = update_transacao_by_user(
            self.db, transacao_id, transacao_in, self.user_id
        )
        if not atualizada:
            return None
        return TransacaoRead.model_validate(atualizada)

    def remover(self, transacao_id: int) -> bool:
        return delete_transacao_by_user(self.db, transacao_id, self.user_id)
