"""
Инициализация и настройка базы данных
"""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from bot.config import settings
from bot.database.models import Base

logger = logging.getLogger(__name__)

# Создаем async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Установите True для отладки SQL запросов
    poolclass=NullPool,  # Для SQLite рекомендуется NullPool
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise


async def get_session() -> AsyncSession:
    """Получение асинхронной сессии базы данных"""
    async with async_session_maker() as session:
        yield session


async def close_db():
    """Закрытие соединения с базой данных"""
    await engine.dispose()
    logger.info("Соединение с базой данных закрыто")
