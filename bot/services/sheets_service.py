"""
Сервис для синхронизации данных с Google Sheets

Автоматически добавляет пользователей и покупки в Google Таблицу
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from bot.config import settings

logger = logging.getLogger(__name__)

# Глобальная переменная для клиента Google Sheets
_sheets_client: Optional[gspread.Client] = None
_worksheet = None


def init_google_sheets():
    """
    Инициализация Google Sheets клиента

    Returns:
        True если инициализация успешна, False в противном случае
    """
    global _sheets_client, _worksheet

    try:
        # Проверяем что credentials файл существует
        if not settings.google_sheets_creds_file:
            logger.warning("Google Sheets credentials файл не указан. Синхронизация отключена.")
            return False

        # Область доступа для Google Sheets API
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        # Авторизация с помощью Service Account
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            settings.google_sheets_creds_file,
            scope
        )

        _sheets_client = gspread.authorize(creds)

        # Открываем таблицу по ID
        spreadsheet = _sheets_client.open_by_key(settings.google_sheet_id)

        # Используем первый лист
        _worksheet = spreadsheet.sheet1

        logger.info(f"Google Sheets успешно инициализирован: {spreadsheet.title}")

        # Проверяем/создаем заголовки
        _ensure_headers()

        return True

    except FileNotFoundError:
        logger.error(f"Credentials файл не найден: {settings.google_sheets_creds_file}")
        return False
    except Exception as e:
        logger.error(f"Ошибка инициализации Google Sheets: {e}", exc_info=True)
        return False


def _ensure_headers():
    """Проверить и создать заголовки таблицы если их нет"""
    global _worksheet

    try:
        # Проверяем первую строку
        first_row = _worksheet.row_values(1)

        # Если таблица пустая - создаем заголовки
        if not first_row:
            headers = [
                'ID',
                'Telegram ID',
                'Имя',
                'Фамилия',
                'Username',
                'Email',
                'Дата регистрации',
                'Подписан',
                'Последнее взаимодействие'
            ]
            _worksheet.append_row(headers)
            logger.info("Заголовки таблицы созданы")

    except Exception as e:
        logger.error(f"Ошибка при создании заголовков: {e}")


async def add_user_to_sheets(
    user_id: int,
    telegram_id: int,
    first_name: str,
    last_name: Optional[str],
    username: Optional[str],
    email: str,
    registration_date: datetime,
    is_subscribed: bool = False
):
    """
    Добавить пользователя в Google Таблицу

    Args:
        user_id: ID пользователя в БД
        telegram_id: Telegram ID
        first_name: Имя
        last_name: Фамилия
        username: Username
        email: Email
        registration_date: Дата регистрации
        is_subscribed: Подписан ли на канал
    """
    global _worksheet

    # Если Google Sheets не инициализирован - пропускаем
    if not _worksheet:
        logger.debug("Google Sheets не инициализирован, пропуск синхронизации")
        return

    try:
        # Форматируем данные
        row = [
            str(user_id),
            str(telegram_id),
            first_name or '',
            last_name or '',
            username or '',
            email,
            registration_date.strftime('%d.%m.%Y %H:%M:%S'),
            'Да' if is_subscribed else 'Нет',
            ''  # Последнее взаимодействие (пока пусто)
        ]

        # gspread — синхронная библиотека, оборачиваем в thread чтобы не блокировать event loop
        await asyncio.to_thread(_worksheet.append_row, row)

        logger.info(f"Пользователь {telegram_id} ({email}) добавлен в Google Sheets")

    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя в Google Sheets: {e}", exc_info=True)


async def update_user_subscription_status(telegram_id: int, is_subscribed: bool):
    """
    Обновить статус подписки пользователя в таблице

    Args:
        telegram_id: Telegram ID пользователя
        is_subscribed: Новый статус подписки
    """
    global _worksheet

    if not _worksheet:
        return

    try:
        # Ищем строку с пользователем по Telegram ID (синхронные вызовы в thread)
        cell = await asyncio.to_thread(_worksheet.find, str(telegram_id))

        if cell:
            # Обновляем столбец "Подписан" (8-й столбец)
            status_text = 'Да' if is_subscribed else 'Нет'
            await asyncio.to_thread(_worksheet.update_cell, cell.row, 8, status_text)
            logger.info(f"Статус подписки обновлен для пользователя {telegram_id}")

    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса подписки: {e}", exc_info=True)


async def add_purchase_to_sheets(
    purchase_id: int,
    telegram_id: int,
    user_name: str,
    email: str,
    webinar_title: str,
    webinar_date: datetime,
    price: float,
    payment_status: str,
    purchase_date: datetime
):
    """
    Добавить покупку в отдельный лист "Покупки"

    Args:
        purchase_id: ID покупки
        telegram_id: Telegram ID пользователя
        user_name: Имя пользователя
        email: Email пользователя
        webinar_title: Название вебинара
        webinar_date: Дата вебинара
        price: Стоимость
        payment_status: Статус оплаты
        purchase_date: Дата покупки
    """
    global _sheets_client

    if not _sheets_client:
        return

    try:
        # Все gspread операции — синхронные, оборачиваем в thread
        def _sync_add_purchase():
            spreadsheet = _sheets_client.open_by_key(settings.google_sheet_id)

            try:
                purchases_sheet = spreadsheet.worksheet("Покупки")
            except gspread.exceptions.WorksheetNotFound:
                purchases_sheet = spreadsheet.add_worksheet(title="Покупки", rows="1000", cols="10")

                headers = [
                    'ID', 'Telegram ID', 'Имя', 'Email', 'Вебинар',
                    'Дата вебинара', 'Цена', 'Статус оплаты', 'Дата покупки'
                ]
                purchases_sheet.append_row(headers)
                logger.info("Создан лист 'Покупки' с заголовками")

            row = [
                str(purchase_id), str(telegram_id), user_name, email,
                webinar_title, webinar_date.strftime('%d.%m.%Y %H:%M'),
                f"{price} ₽", payment_status,
                purchase_date.strftime('%d.%m.%Y %H:%M:%S')
            ]
            purchases_sheet.append_row(row)

        await asyncio.to_thread(_sync_add_purchase)

        logger.info(f"Покупка #{purchase_id} добавлена в Google Sheets")

    except Exception as e:
        logger.error(f"Ошибка при добавлении покупки в Google Sheets: {e}", exc_info=True)
