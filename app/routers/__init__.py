from app.routers.bancos import router as bancos_router
from app.routers.cartoes import router as cartoes_router
from app.routers.categorias import router as categorias_router
from app.routers.contas import router as contas_router
from app.routers.faturas import router as faturas_router
from app.routers.sub_categorias import router as sub_categorias_router
from app.routers.transacoes import router as transacoes_router
from app.routers.transacoes_parcelas import router as transacoes_parcelas_router
from app.routers.usuarios import router as usuarios_router

routers = [
    (bancos_router, "/api/v1/bancos", ["Bancos"]),
    (categorias_router, "/api/v1/categorias", ["Categorias"]),
    (cartoes_router, "/api/v1/cartoes", ["Cartoes"]),
    (contas_router, "/api/v1/contas", ["Contas"]),
    (faturas_router, "/api/v1/faturas", ["Faturas"]),
    (sub_categorias_router, "/api/v1/sub-categorias", ["SubCategorias"]),
    (transacoes_parcelas_router, "/api/v1/transacoes-parcelas", ["TransacoesParcelas"]),
    (transacoes_router, "/api/v1/transacoes", ["Transacoes"]),
    (usuarios_router, "/api/v1/usuarios", ["Usuarios"]),
]
