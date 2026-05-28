from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import sys

from app.database.session import create_tables, verify_database_connection, close_database
from app.middleware.error_handler import (
    global_exception_handler,
    validation_exception_handler,
    db_exception_handler,
    logging_middleware,
)
from app.routes import auth, users, meals, analytics, predict, food, foods, ai, notifications
from app.services.food_service import food_service
import asyncio

# ── Logging setup ──────────────────────────────────────────────────────────────
logger.remove()
logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")
logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="DEBUG")

# ── App factory ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CalorieTracker API",
    description="AI-powered calorie tracking backend with Indian Food ML models",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request logging middleware ─────────────────────────────────────────────────
app.middleware("http")(logging_middleware)

# ── Exception handlers ─────────────────────────────────────────────────────────
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, db_exception_handler)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(meals.router)
app.include_router(analytics.router)
app.include_router(predict.router)
app.include_router(food.router)
app.include_router(foods.router)
app.include_router(ai.router)
app.include_router(notifications.router)


# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("Starting CalorieTracker API...")
    # Load potentially heavy dataset/ML artifacts off the event loop
    try:
        await asyncio.to_thread(food_service.initialize)
        logger.info(f"Food dataset loaded: {food_service.food_count} items (ML ready: {food_service.ml_ready})")
    except Exception as exc:
        logger.error(f"Food service initialization failed: {exc}")
    try:
        await verify_database_connection()
        await create_tables()
        logger.info("Database tables ready.")
    except Exception as exc:
        logger.error(f"Database startup failed: {exc}")
        raise


@app.on_event("shutdown")
async def shutdown():
    await close_database()


@app.get("/health", tags=["Health"])
async def health():
    db_ok = False
    try:
        await verify_database_connection()
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "version": "1.0.0",
        "foods_loaded": food_service.loaded,
        "food_count": food_service.food_count if food_service.loaded else 0,
        "ml_ready": food_service.ml_ready,
    }
