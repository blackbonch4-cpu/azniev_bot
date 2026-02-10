"""
Планировщик задач для автоматических напоминаний

Использует APScheduler для периодической проверки и отправки напоминаний.
"""

import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from bot.database.db_setup import async_session_maker
from bot.database import crud
from bot.texts import messages
from bot.config import settings

logger = logging.getLogger(__name__)

# Глобальный экземпляр планировщика
scheduler = AsyncIOScheduler()


async def check_24h_reminders(bot: Bot):
    """
    Проверить и отправить напоминания за 24 часа до вебинара

    Вызывается каждые 10 минут планировщиком
    """
    logger.info("Проверка напоминаний за 24 часа...")

    async with async_session_maker() as session:
        try:
            # Получаем покупки для напоминания за 24 часа
            purchases = await crud.get_purchases_for_reminder(
                session=session,
                hours_before=24,
                notification_field="notification_24h_sent"
            )

            if not purchases:
                logger.debug("Нет покупок для напоминания за 24 часа")
                return

            logger.info(f"Найдено {len(purchases)} покупок для напоминания за 24 часа")

            # Отправляем напоминания
            for purchase in purchases:
                try:
                    user = purchase.user
                    webinar = purchase.webinar

                    # Форматируем дату и время
                    date_str = webinar.event_datetime.strftime("%d.%m.%Y")
                    time_str = webinar.event_datetime.strftime("%H:%M")

                    # Формируем сообщение
                    reminder_message = messages.REMINDER_24H.format(
                        title=webinar.title,
                        date=date_str,
                        time=time_str,
                        location=webinar.location or "Онлайн"
                    )

                    # Отправляем напоминание
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=reminder_message
                    )

                    logger.info(f"Напоминание за 24ч отправлено пользователю {user.telegram_id}")

                    # Помечаем что напоминание отправлено
                    await crud.mark_notification_sent(session, purchase.id, "24h")

                except Exception as e:
                    logger.error(
                        f"Ошибка при отправке напоминания за 24ч пользователю {purchase.user.telegram_id}: {e}",
                        exc_info=True
                    )

        except Exception as e:
            logger.error(f"Ошибка при проверке напоминаний за 24 часа: {e}", exc_info=True)


async def check_1h_reminders(bot: Bot):
    """
    Проверить и отправить напоминания за 1 час до вебинара

    Вызывается каждые 10 минут планировщиком
    """
    logger.info("Проверка напоминаний за 1 час...")

    async with async_session_maker() as session:
        try:
            # Получаем покупки для напоминания за 1 час
            purchases = await crud.get_purchases_for_reminder(
                session=session,
                hours_before=1,
                notification_field="notification_1h_sent"
            )

            if not purchases:
                logger.debug("Нет покупок для напоминания за 1 час")
                return

            logger.info(f"Найдено {len(purchases)} покупок для напоминания за 1 час")

            # Отправляем напоминания
            for purchase in purchases:
                try:
                    user = purchase.user
                    webinar = purchase.webinar

                    # Форматируем дату и время
                    date_str = webinar.event_datetime.strftime("%d.%m.%Y")
                    time_str = webinar.event_datetime.strftime("%H:%M")

                    # Формируем сообщение
                    reminder_message = messages.REMINDER_1H.format(
                        title=webinar.title,
                        date=date_str,
                        time=time_str,
                        location=webinar.location or "Онлайн"
                    )

                    # Отправляем напоминание
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=reminder_message
                    )

                    logger.info(f"Напоминание за 1ч отправлено пользователю {user.telegram_id}")

                    # Помечаем что напоминание отправлено
                    await crud.mark_notification_sent(session, purchase.id, "1h")

                except Exception as e:
                    logger.error(
                        f"Ошибка при отправке напоминания за 1ч пользователю {purchase.user.telegram_id}: {e}",
                        exc_info=True
                    )

        except Exception as e:
            logger.error(f"Ошибка при проверке напоминаний за 1 час: {e}", exc_info=True)


def start_scheduler(bot: Bot):
    """
    Запустить планировщик задач

    Args:
        bot: Экземпляр бота для отправки сообщений
    """
    logger.info("Запуск планировщика задач...")

    # Добавляем задачу проверки напоминаний за 24 часа
    scheduler.add_job(
        check_24h_reminders,
        trigger=IntervalTrigger(minutes=settings.reminder_check_interval),
        args=[bot],
        id="check_24h_reminders",
        name="Проверка напоминаний за 24 часа",
        replace_existing=True
    )

    # Добавляем задачу проверки напоминаний за 1 час
    scheduler.add_job(
        check_1h_reminders,
        trigger=IntervalTrigger(minutes=settings.reminder_check_interval),
        args=[bot],
        id="check_1h_reminders",
        name="Проверка напоминаний за 1 час",
        replace_existing=True
    )

    # Запускаем планировщик
    scheduler.start()

    logger.info(
        f"Планировщик запущен. Интервал проверки: {settings.reminder_check_interval} минут"
    )


def stop_scheduler():
    """
    Остановить планировщик задач
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Планировщик остановлен")
