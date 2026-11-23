from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.apis import lote_api, pedido_api, auth_api

app = FastAPI(title="WankaAgro Track API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api.router)
app.include_router(lote_api.router)
app.include_router(pedido_api.router)