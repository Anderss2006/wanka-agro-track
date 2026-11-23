from fastapi import APIRouter
from app.schemas.auth import LoginRequest
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

@router.post("/login")
def login(datos: LoginRequest):
    return auth_service.autenticar_usuario(datos)