"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models  # noqa: F401 — register ORM metadata
from app.api.routes import router
from app.config import get_settings
from app.db import Base, engine
from app.errors import AppError

API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_settings()  # load .env + export OPENROUTER_API_KEY for llmcall
    # Dev convenience: create tables if missing. Alembic owns schema in real flows.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Zero Sum 2027", version="0.1.0", lifespan=lifespan)
get_settings()  # load env early for CORS + downstream imports
_cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.include_router(router, prefix=API_PREFIX)


def _error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
    code = "http_error" if exc.status_code != 404 else "not_found"
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content=_error_body(code, detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=_error_body("validation_error", str(exc.errors())),
    )


@app.get(f"{API_PREFIX}/health")
async def health():
    return {"status": "ok"}
