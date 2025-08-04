from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from utils.auditoria_utils import registrar_auditoria, serialize_mapped
from utils.model_utils import apply_update_fields

from app import errors, models
from app.crud import banco as banco_crud
from app.schemas.banco import Banco, BancoCreate

BancoModel = models.Banco

err_banco = errors.banco


class BancoService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(self, skip: int = 0, limit: int = 100) -> list[Banco]:
        bancos = banco_crud.get_bancos(self.db, skip=skip, limit=limit)
        return [Banco.model_validate(b) for b in bancos]

    def buscar_por_id(self, banco_id: int) -> Banco | None:
        banco = banco_crud.get_banco(self.db, banco_id)
        return Banco.model_validate(banco) if banco else None

    def criar(self, dados: BancoCreate, user_id: int) -> Banco:
        # Verifica por CNPJ (inclusive deletados)
        if dados.cnpj or dados.cnpj == "":
            banco = banco_crud.get_banco_por_cnpj_todos(self.db, dados.cnpj)
            if banco:
                if banco.deleted_at:
                    raise HTTPException(
                        status_code=400,
                        detail=(err_banco.JA_DESATIVADO.format(id=banco.id)),
                    )
                raise HTTPException(
                    status_code=400,
                    detail=err_banco.JA_EXISTE.format(id=banco.id, campo="CNPJ"),
                )

        # Verifica por código
        banco = banco_crud.get_banco_por_codigo_todos(self.db, dados.codigo)
        if banco:
            if banco.deleted_at:
                banco_id = banco.id
                raise HTTPException(
                    status_code=400,
                    detail=err_banco.JA_DESATIVADO.format(id=banco.id),
                )
            raise HTTPException(
                status_code=400,
                detail=err_banco.JA_EXISTE.format(id=banco.id, campo="Código"),
            )

        # Verifica por nome
        banco = banco_crud.get_banco_por_nome_todos(self.db, dados.nome)
        if banco:
            if banco.deleted_at:
                banco_id = banco.id
                raise HTTPException(
                    status_code=400,
                    detail=err_banco.JA_DESATIVADO.format(id=banco_id),
                )
            raise HTTPException(
                status_code=400,
                detail=err_banco.JA_EXISTE.format(id=banco.id, campo="Nome"),
            )

        banco = banco_crud.create_banco(self.db, dados, user_id)

        registrar_auditoria(
            db=self.db,
            tabela="bancos",
            registro_id=banco.id,
            acao="create",
            user_id=user_id,
            dados_depois=dados.model_dump(),
        )
        self.db.commit()
        self.db.refresh(banco)
        return Banco.model_validate(banco)

    def atualizar(self, banco_id: int, dados: BancoCreate, user_id: int) -> Banco:
        banco = banco_crud.get_banco(self.db, banco_id)
        if not banco:
            raise HTTPException(status_code=404, detail=err_banco.NAO_ENCONTRADO)

        dados_antes = serialize_mapped(banco)

        campos_alterados = apply_update_fields(
            model=banco, data=dados, fields=["nome", "codigo", "cnpj", "site", "ativo"]
        )

        if not campos_alterados:
            return Banco.model_validate(banco)

        banco.updated_by = user_id
        banco.updated_at = datetime.now(UTC)

        registrar_auditoria(
            db=self.db,
            tabela="bancos",
            registro_id=banco.id,
            acao="update",
            user_id=user_id,
            dados_antes=dados_antes,
            dados_input=dados.model_dump(exclude_none=False),
            dados_depois=serialize_mapped(banco),
        )

        self.db.commit()
        self.db.refresh(banco)
        return Banco.model_validate(banco)

    def remover(self, banco_id: int, user_id: int) -> None:
        banco = banco_crud.get_banco(self.db, banco_id)
        if not banco:
            raise HTTPException(status_code=404, detail=err_banco.NAO_ENCONTRADO)

        banco.deleted_by = user_id
        banco.deleted_at = datetime.now(UTC)
        banco.ativo = False

        banco = banco_crud.soft_delete_banco(self.db, banco)

        registrar_auditoria(
            db=self.db,
            tabela="bancos",
            registro_id=banco.id,
            acao="delete",
            user_id=user_id,
            dados_antes=serialize_mapped(banco),
        )

        self.db.commit()
