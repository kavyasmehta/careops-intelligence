"""CareOps Intelligence API entrypoint.

Portfolio demonstration using synthetic data. Not intended for clinical
use or storage of protected health information.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.logging import configure_logging, get_logger
from app.db.indexes import ensure_indexes
from app.db.mongo import close_mongo, get_database, ping_mongo
from app.db.neo4j import close_neo4j
from app.routers import (
    alerts,
    analytics,
    appointments,
    audit_logs,
    authorizations,
    case_notes,
    clients,
    dashboard,
    eligibility,
    graph,
    health,
    tasks,
    users,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("CareOps Intelligence API starting up")
    if await ping_mongo():
        await ensure_indexes(get_database())
        logger.info("MongoDB indexes ensured")
    else:
        logger.warning("MongoDB unreachable at startup — skipping index setup")
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


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": {"code": 404, "message": exc.message, "details": None}})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"error": {"code": 409, "message": exc.message, "details": None}})


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"error": {"code": 422, "message": exc.message, "details": None}})


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
app.include_router(clients.router)
app.include_router(eligibility.router)
app.include_router(authorizations.router)
app.include_router(appointments.router)
app.include_router(alerts.router)
app.include_router(tasks.router)
app.include_router(case_notes.router)
app.include_router(audit_logs.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(graph.router)
app.include_router(analytics.router)
