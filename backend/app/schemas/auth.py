from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    dni: str = Field(..., pattern=r"^\d{8}$", description="DNI de 8 dígitos")
    clave: str = Field(..., min_length=4, description="Número de celular o contraseña registrada")