from app.schemas.base import BaseSchema


class EvolucaoGastoResponse(BaseSchema):
    ano: int
    mes: int
    valor: float
    periodo: str
