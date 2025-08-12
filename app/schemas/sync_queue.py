from datetime import datetime
from typing import Literal
from uuid import UUID

from app.schemas.base import BaseSchema


class SyncQueueBase(BaseSchema):
    user_id: UUID
    device_id: str
    entidade: str
    acao: Literal["create", "update", "delete"]
    payload: dict[str, str]
    status: Literal["pendente", "processado", "erro"] = "pendente"
    tentativa: int = 0


class SyncQueueCreate(SyncQueueBase):
    pass


class SyncQueue(SyncQueueBase):
    id: UUID
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True  # permite converter de ORM do SQLAlchemy
