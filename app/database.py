"""
Database Configuration

Async PostgreSQL connection using SQLAlchemy 2.0.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Only create engine if DATABASE_URL is configured
engine = None
AsyncSessionLocal = None

if settings.DATABASE_URL:
    # Convert postgres:// to postgresql+asyncpg:// if needed
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        pool_size=20,
        max_overflow=10,
    )

    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

Base = declarative_base()


async def get_db():
    """Dependency to get database session."""
    if AsyncSessionLocal is None:
        yield None
        return

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    if engine is None:
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection."""
    if engine is not None:
        await engine.dispose()
