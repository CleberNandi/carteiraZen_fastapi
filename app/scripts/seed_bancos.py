from app.db.session import SessionLocal
from app.models.banco import Banco

BANCOS_PRINCIPAIS = [
    {
        "nome": "Banco do Brasil",
        "codigo": "001",
        "ispb": "00000000",
        "cnpj": "00.000.000/0001-91",
        "site": "https://www.bb.com.br",
        "ativo": True,
    },
    {
        "nome": "Bradesco",
        "codigo": "237",
        "ispb": "60746948",
        "cnpj": "60.746.948/0001-12",
        "site": "https://www.bradesco.com.br",
        "ativo": True,
    },
    {
        "nome": "Itaú Unibanco",
        "codigo": "341",
        "ispb": "60701190",
        "cnpj": "60.701.190/0001-04",
        "site": "https://www.itau.com.br",
        "ativo": True,
    },
    {
        "nome": "Caixa Econômica Federal",
        "codigo": "104",
        "ispb": "00360305",
        "cnpj": "00.360.305/0001-04",
        "site": "https://www.caixa.gov.br",
        "ativo": True,
    },
    {
        "nome": "Santander",
        "codigo": "033",
        "ispb": "90400888",
        "cnpj": "90.400.888/0001-42",
        "site": "https://www.santander.com.br",
        "ativo": True,
    },
    {
        "nome": "Banco Inter",
        "codigo": "077",
        "ispb": "00416968",
        "cnpj": "00.416.968/0001-01",
        "site": "https://www.bancointer.com.br",
        "ativo": True,
    },
    {
        "nome": "Nubank",
        "codigo": "260",
        "ispb": "18236120",
        "cnpj": "18.236.120/0001-58",
        "site": "https://www.nubank.com.br",
        "ativo": True,
    },
    {
        "nome": "Banco Original",
        "codigo": "212",
        "ispb": "92894922",
        "cnpj": "92.894.922/0001-08",
        "site": "https://www.original.com.br",
        "ativo": True,
    },
    {
        "nome": "Banco Safra",
        "codigo": "422",
        "ispb": "58160789",
        "cnpj": "58.160.789/0001-28",
        "site": "https://www.safra.com.br",
        "ativo": True,
    },
    {
        "nome": "BTG Pactual",
        "codigo": "208",
        "ispb": "30306294",
        "cnpj": "30.306.294/0001-45",
        "site": "https://www.btgpactual.com",
        "ativo": True,
    },
]


def seed_bancos() -> None:
    db = SessionLocal()
    for banco in BANCOS_PRINCIPAIS:
        exists = db.query(Banco).filter(Banco.codigo == banco["codigo"]).first()
        if not exists:
            db.add(Banco(**banco))
    db.commit()
    db.close()


if __name__ == "__main__":
    seed_bancos()
    print("Seed de bancos executado com sucesso!")
