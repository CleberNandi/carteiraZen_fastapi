# app/api/routes/nfce.py
from fastapi import APIRouter, HTTPException

from app.schemas.nfce import NFCEData, NFCERequest
from app.services.nfce_service import extrair_dados_nfce

router = APIRouter(prefix="/nfce", tags=["NFCe"])


@router.post("/ler/", response_model=NFCEData)
async def ler_nfce(request: NFCERequest) -> NFCEData:
    try:
        return extrair_dados_nfce(request.html)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Erro ao processar NFCe: {e!s}"
        ) from e
