from fastapi import APIRouter
from app.schemas.lote import LoteCreate
from app.schemas.productor import ProductorCreate
from app.services import lote_service

router = APIRouter(prefix="/api", tags=["Ofertas, Productores y Catálogos"])

@router.get("/lotes")
def get_lotes():
    return lote_service.listar_lotes_disponibles()

@router.get("/catalogos")
def get_catalogos():
    return lote_service.obtener_catalogos()

@router.post("/lotes", status_code=201)
def post_lote(lote: LoteCreate):
    return lote_service.publicar_lote(lote)

@router.post("/productores", status_code=201)
def post_productor(productor: ProductorCreate):
    return lote_service.registrar_productor(productor)