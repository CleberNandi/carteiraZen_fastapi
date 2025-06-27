from collections.abc import Generator, Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import banco as crud_banco
from app.db.session import SessionLocal
from app.schemas.banco import Banco, BancoCreate

router = APIRouter()


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/bancos/", response_model=list[Banco], tags=["Bancos"])
def read_bancos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Banco]:
    return crud_banco.get_bancos(db, skip=skip, limit=limit)


@router.get("/bancos/{banco_id}", response_model=Banco, tags=["Bancos"])
def read_banco(banco_id: int, db: Session = Depends(get_db)) -> Banco:  # noqa: B008
    db_banco = crud_banco.get_banco(db, banco_id=banco_id)
    if db_banco is None:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    return db_banco


@router.post("/bancos/", response_model=Banco, tags=["Bancos"])
def create_banco(
    banco: BancoCreate,
    user_id: int,  # Novo parâmetro obrigatório
    db: Session = Depends(get_db),  # noqa: B008
) -> Banco:
    db_banco = crud_banco.get_banco_by_codigo(db, codigo=banco.codigo)
    if db_banco:
        raise HTTPException(status_code=400, detail="Código de banco já cadastrado")
    return crud_banco.create_banco(db=db, banco=banco, user_id=user_id)


@router.put("/bancos/{banco_id}", response_model=Banco, tags=["Bancos"])
def update_banco(
    banco_id: int,
    banco: BancoCreate,
    user_id: int,  # Novo parâmetro obrigatório
    db: Session = Depends(get_db),  # noqa: B008
) -> Banco:
    db_banco = crud_banco.get_banco(db, banco_id=banco_id)
    if db_banco is None:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    banco_atualizado = crud_banco.update_banco(
        db=db, banco_id=banco_id, banco=banco, user_id=user_id
    )
    if banco_atualizado is None:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    return banco_atualizado


@router.delete("/bancos/{banco_id}", tags=["Bancos"])
def delete_banco(
    banco_id: int,
    user_id: int,  # Novo parâmetro obrigatório
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    sucesso = crud_banco.delete_banco(db=db, banco_id=banco_id, user_id=user_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    return {"detail": "Banco removido com sucesso"}
