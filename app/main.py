from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

from app.core import get_settings, init_gateway_client, shutdown_gateway_client
from app.route import router as api_router

settings = get_settings()
tags_metadata = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_gateway_client(app)
    yield
    await shutdown_gateway_client(app)


app = FastAPI(
    openapi_tags=tags_metadata,
    title="АПИ для работы с отчетами ЕВМИАС",
    description="АПИ для работы с отчетами ЕВМИАС",
    lifespan=lifespan,
    version="0.0.1"
)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)


app.include_router(api_router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# 2. Роут для главной страницы
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))