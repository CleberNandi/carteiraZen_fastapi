# app/scripts/seed_bancos.py
import json
from pathlib import Path

from app.db.session import SessionLocal
from app.schemas.banco import BancoCreate
from app.services.bancos import BancoService


def seed_bancos(user_id: int | None = None) -> None:
    db = SessionLocal()

    # Caminho do JSON oficial FEBRABAN
    json_path = Path("app/scripts/bancos.json")
    with json_path.open("r", encoding="utf-8-sig") as f:
        bancos = json.load(f)

    for banco in bancos:
        codigo = banco.get("COMPE")
        banco_existe = BancoService(db).buscar_por_id(codigo)
        # Verifica se já existe pelo código
        if not banco_existe:
            obj = BancoCreate(
                nome=banco.get("ShortName"),
                codigo=codigo,
                ispb=banco.get("ISPB"),
                cnpj=banco.get("Document"),
                site=banco.get("Url"),
            )
            BancoService(db).criar(obj, user_id)

    db.close()
