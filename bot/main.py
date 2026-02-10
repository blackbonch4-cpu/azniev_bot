"""
Главный файл бота - точка входа

Запуск: python -m bot.main
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.database.db_setup import init_db, close_db

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""

    # Инициализация бота и диспетчера
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    dp = Dispatcher()

    try:
        # Инициализация базы данных
        logger.info("Инициализация базы данных...")
        await init_db()

        # Инициализация Google Sheets
        logger.info("Инициализация Google Sheets...")
        from bot.services import sheets_service
        sheets_initialized = sheets_service.init_google_sheets()
        if sheets_initialized:
            logger.info("Google Sheets успешно инициализирован")
        else:
            logger.warning("Google Sheets не инициализирован - синхронизация отключена")

        # Регистрация middlewares
        from bot.middlewares.subscription_check import SubscriptionCheckMiddleware
        dp.message.middleware(SubscriptionCheckMiddleware())
        dp.callback_query.middleware(SubscriptionCheckMiddleware())
        logger.info("Middlewares зарегистрированы")

        # Регистрация хэндлеров
        from bot.handlers import start, webinar, payments, support, admin
        dp.include_router(start.router)
        dp.include_router(webinar.router)
        dp.include_router(payments.router)
        dp.include_router(support.router)
        dp.include_router(admin.router)
        logger.info("Handlers зарегистрированы")

        # Запуск планировщика задач
        from bot.scheduler.tasks import start_scheduler
        start_scheduler(bot)
        logger.info("Планировщик задач запущен")

        logger.info("Бот успешно запущен!")

        # Запуск API сервера и polling параллельно
        from api.server import run_api_server

        api_task = asyncio.create_task(run_api_server(bot))
        polling_task = asyncio.create_task(dp.start_polling(bot))

        # Ждать завершения обеих задач
        await asyncio.gather(api_task, polling_task)

    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        # Остановка планировщика
        from bot.scheduler.tasks import stop_scheduler
        stop_scheduler()

        # Закрытие соединений
        await close_db()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот завершил работу")
