import time
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger


async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions — returns clean JSON, logs full traceback."""
    logger.exception(f"Unhandled error on {request.method} {request.url}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Returns readable validation errors instead of FastAPI's default verbose format."""
    errors = [{"field": e["loc"][-1], "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})


async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error on {request.method} {request.url}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Database error"})


async def logging_middleware(request: Request, call_next):
    """Log every request with method, path, status code, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = round((time.perf_counter() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response
