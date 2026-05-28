import ssl
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from loguru import logger
from app.config.settings import get_settings

settings = get_settings()
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")


def _build_engine():
    if _is_sqlite:
        return create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False},
        )

    connect_args = {}
    if "supabase" in settings.DATABASE_URL.lower() or "ssl=require" in settings.DATABASE_URL.lower():
        connect_args["ssl"] = ssl.create_default_context()

    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def verify_database_connection() -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("PostgreSQL connection verified")


async def create_tables():
    # Import models so metadata is populated
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    await engine.dispose()
    logger.info("Database engine disposed")
