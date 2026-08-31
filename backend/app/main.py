"""CareOps Intelligence API entrypoint.

Portfolio demonstration using synthetic data. Not intended for clinical
use or storage of protected health information.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.mongo import close_mongo
from app.db.neo4j import close_neo4j
from app.routers import health

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("CareOps Intelligence API starting up")
    yield
    await close_mongo()
    await close_neo4j()
    logger.info("CareOps Intelligence API shut down")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Healthcare operations management and analytics platform (portfolio demo). "
        "Portfolio demonstration using synthetic data. Not intended for clinical use "
        "or storage of protected health information."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail, "details": None}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": 500, "message": "Internal server error", "details": None}},
    )


@app.get("/")
async def root():
    return {
        "data": {
            "name": settings.app_name,
            "disclaimer": (
                "Portfolio demonstration using synthetic data. Not intended for "
                "clinical use or storage of protected health information."
            ),
        }
    }


app.include_router(health.router)
