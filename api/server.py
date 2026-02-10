"""
API сервер на aiohttp

Запускается параллельно с Telegram bot polling
"""

import logging
from aiohttp import web
import aiohttp_cors
from aiogram import Bot

from api.routes import setup_routes
from bot.config import settings

logger = logging.getLogger(__name__)


async def run_api_server(bot: Bot):
    """
    Запустить API сервер

    Args:
        bot: Instance бота для отправки сообщений в поддержку
    """
    app = web.Application()

    # Сохранить bot в app для использования в handlers
    app['bot'] = bot

    # Настроить маршруты
    setup_routes(app)

    # Настроить CORS
    # allow_credentials нельзя использовать с wildcard "*" — браузер блокирует такие ответы
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=False,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })

    # Применить CORS ко всем маршрутам
    for route in list(app.router.routes()):
        try:
            cors.add(route)
        except Exception:
            # Некоторые маршруты могут не поддерживать CORS
            pass

    logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")

    # Запустить сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.api_host, settings.api_port)
    await site.start()

    logger.info(f"API server started successfully on http://{settings.api_host}:{settings.api_port}")

    # Держать сервер запущенным
    try:
        while True:
            await asyncio.sleep(3600)  # Проверять каждый час
    except asyncio.CancelledError:
        logger.info("API server stopping...")
        await runner.cleanup()


# Для импорта
import asyncio
