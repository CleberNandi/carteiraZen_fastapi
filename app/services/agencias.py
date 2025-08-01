from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from utils.auditoria_utils import registrar_auditoria, serialize_mapped
from utils.model_utils import apply_update_fields

from app import models
from app.crud import agencia as agencia_crud
from app.schemas.agencia import Agencia, AgenciaCreate

AgenciaModel = models.Agencia


class AgenciaService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, skip: int = 0, limit: int = 100) -> list[Agencia]:
        agencias = agencia_crud.get_agencias(self.db, skip=skip, limit=limit)
        return [Agencia.model_validate(a) for a in agencias]

    def buscar_por_id(self, agencia_id: int) -> Agencia | None:
        agencia = agencia_crud.get_agencia(self.db, agencia_id)
        return Agencia.model_validate(agencia) if agencia else None

    def criar(self, dados: AgenciaCreate, user_id: int) -> Agencia:
        existente = agencia_crud.get_agencia_por_numero_banco(
            self.db, dados.numero, dados.banco_id
        )
        if existente:
            raise HTTPException(
                status_code=400, detail="Agência já existe para este banco."
            )

        agencia = agencia_crud.create_agencia(self.db, dados, user_id)

        registrar_auditoria(
            db=self.db,
            tabela="agencias",
            registro_id=agencia.id,
            acao="create",
            user_id=user_id,
            dados_depois=dados.model_dump(),
        )

        self.db.commit()
        self.db.refresh(agencia)
        return Agencia.model_validate(agencia)

    def atualizar(self, agencia_id: int, dados: AgenciaCreate, user_id: int) -> Agencia:
        agencia = agencia_crud.get_agencia(self.db, agencia_id)
        if not agencia:
            raise HTTPException(status_code=404, detail="Agência não encontrada")

        dados_antes = serialize_mapped(agencia)

        campos_alterados = apply_update_fields(
            model=agencia,
            data=dados,
            fields=["nome", "digito", "tipo", "ativo", "saldo_inicial"],
        )

        if not campos_alterados:
            return Agencia.model_validate(agencia)

        agencia.updated_by = user_id
        agencia.updated_at = datetime.now(UTC)

        registrar_auditoria(
            db=self.db,
            tabela="agencias",
            registro_id=agencia.id,
            acao="update",
            user_id=user_id,
            dados_antes=dados_antes,
            dados_input=dados.model_dump(exclude_none=False),
            dados_depois=serialize_mapped(agencia),
        )

        self.db.commit()
        self.db.refresh(agencia)
        return Agencia.model_validate(agencia)

    def remover(self, agencia_id: int, user_id: int) -> None:
        agencia = agencia_crud.get_agencia(self.db, agencia_id)
        if not agencia:
            raise HTTPException(status_code=404, detail="Agência não encontrada")

        agencia.deleted_by = user_id
        agencia.deleted_at = datetime.now(UTC)
        agencia.ativo = False

        agencia = agencia_crud.soft_delete_agencia(self.db, agencia)

        registrar_auditoria(
            db=self.db,
            tabela="agencias",
            registro_id=agencia.id,
            acao="delete",
            user_id=user_id,
            dados_antes=serialize_mapped(agencia),
        )

        self.db.commit()
