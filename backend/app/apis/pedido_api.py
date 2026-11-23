from fastapi import APIRouter, Query
from app.schemas.pedido import PedidoCreate
from app.services import pedido_service

router = APIRouter(prefix="/api", tags=["Pedidos y Reservas"])

@router.post("/pedidos", status_code=201)
def post_pedido(pedido: PedidoCreate):
    return pedido_service.crear_pedido(pedido)

@router.get("/pedidos/usuario/{id_usuario}")
def get_pedidos_usuario(id_usuario: int, rol: str = Query(..., description="PRODUCTOR o COMPRADOR")):
    return pedido_service.listar_pedidos_usuario(id_usuario, rol)