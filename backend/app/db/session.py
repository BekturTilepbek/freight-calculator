from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Engine — одно подключение на все приложение
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # True — будет печатать все SQL-запросы (полезно при отладке)
    pool_pre_ping=True,  # автоматически проверяет, что соединение живо
)

# Фабрика сессий — каждый запрос получает свою сессию
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # объекты остаются доступны после commit
    autoflush=False,
)


async def get_db():
    """
    FastAPI dependency: открывает сессию на время запроса и закрывает после.
    Использование: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()