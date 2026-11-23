from pydantic import BaseModel, Field
from datetime import date

class LoteCreate(BaseModel):
    id_productor: int = Field(..., gt=0, description="ID del agricultor registrado")
    id_producto: int = Field(..., gt=0, description="ID del producto del catálogo")
    precio_unitario: float = Field(..., gt=0, description="El precio debe ser mayor a 0")
    stock_disponible: float = Field(..., gt=0, description="El stock inicial debe ser mayor a 0")
    fecha_cosecha: date
    punto_entrega: str = Field(..., min_length=5, max_length=150)