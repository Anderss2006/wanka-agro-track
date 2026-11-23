from pydantic import BaseModel, Field

class PedidoCreate(BaseModel):
    id_comprador: int = Field(..., gt=0)
    id_lote: int = Field(..., gt=0)
    cantidad: float = Field(..., gt=0, description="Cantidad a reservar")