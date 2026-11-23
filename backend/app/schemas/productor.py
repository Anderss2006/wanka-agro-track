from pydantic import BaseModel, Field

class ProductorCreate(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=80)
    apellidos: str = Field(..., min_length=2, max_length=80)
    dni: str = Field(..., pattern=r"^\d{8}$", description="DNI de 8 dígitos")
    telefono: str = Field(..., pattern=r"^\d{9}$", description="Celular de 9 dígitos")
    id_distrito: int = Field(..., gt=0, description="Distrito de procedencia en el Valle del Mantaro")