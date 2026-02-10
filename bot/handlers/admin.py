"""
Handler для админ панели

Обрабатывает:
- Команду /setparams - создание нового вебинара
- Команду /stats - статистика
- FSM диалог для создания вебинара
"""

import logging
from datetime import datetime
from decimal import Decimal
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.database.db_setup import async_session_maker
from bot.database import crud
from bot.states.admin import AdminWebinarStates
from bot.utils import validators
from bot.utils.keyboards import get_admin_panel_keyboard
from bot.texts import messages
from bot.middlewares.admin_check import AdminCheckMiddleware

logger = logging.getLogger(__name__)

# Создаем router для этого модуля
router = Router(name='admin')

# Применяем middleware проверки прав администратора ко всему router'у
router.message.middleware(AdminCheckMiddleware())
router.callback_query.middleware(AdminCheckMiddleware())


@router.message(Command("setparams"))
async def cmd_setparams(message: Message):
    """
    Команда /setparams - показать админ панель
    """
    user_id = message.from_user.id

    logger.info(f"Команда /setparams от администратора {user_id}")

    # Показываем админ панель
    await message.answer(
        messages.ADMIN_PANEL,
        reply_markup=get_admin_panel_keyboard()
    )


@router.callback_query(F.data == "admin_create_webinar")
async def callback_create_webinar(callback: CallbackQuery, state: FSMContext):
    """
    Начать создание нового вебинара
    """
    logger.info(f"Администратор {callback.from_user.id} начал создание вебинара")

    # Отправляем инструкцию
    await callback.message.answer(messages.ADMIN_CREATE_WEBINAR)

    # Устанавливаем первое состояние FSM
    await state.set_state(AdminWebinarStates.waiting_for_title)

    await callback.answer()


@router.message(AdminWebinarStates.waiting_for_title)
async def process_webinar_title(message: Message, state: FSMContext):
    """
    Обработка названия вебинара
    """
    title = message.text.strip()

    logger.info(f"Получено название вебинара: {title}")

    # Валидация названия
    if len(title) < 5:
        await message.answer("❌ Название слишком короткое! Минимум 5 символов.")
        return

    if len(title) > 200:
        await message.answer("❌ Название слишком длинное! Максимум 200 символов.")
        return

    # Сохраняем название в FSM storage
    await state.update_data(title=title)

    # Переходим к следующему шагу - описание
    await message.answer(messages.ADMIN_WEBINAR_DESCRIPTION)
    await state.set_state(AdminWebinarStates.waiting_for_description)


@router.message(AdminWebinarStates.waiting_for_description)
async def process_webinar_description(message: Message, state: FSMContext):
    """
    Обработка описания вебинара
    """
    description = message.text.strip()

    logger.info(f"Получено описание вебинара: {description[:50]}...")

    # Проверка на команду пропуска
    if description.lower() == "/skip":
        description = None
        logger.info("Описание пропущено")
    else:
        # Валидация описания
        if len(description) > 1000:
            await message.answer("❌ Описание слишком длинное! Максимум 1000 символов.")
            return

    # Сохраняем описание в FSM storage
    await state.update_data(description=description)

    # Переходим к следующему шагу - дата и время
    await message.answer(messages.ADMIN_WEBINAR_DATE)
    await state.set_state(AdminWebinarStates.waiting_for_date)


@router.message(AdminWebinarStates.waiting_for_date)
async def process_webinar_date(message: Message, state: FSMContext):
    """
    Обработка даты и времени вебинара
    """
    date_str = message.text.strip()

    logger.info(f"Получена дата: {date_str}")

    # Валидация даты
    event_datetime = validators.validate_datetime(date_str)

    if not event_datetime:
        await message.answer(messages.ADMIN_INVALID_DATE)
        return

    # Проверяем что дата в будущем
    if event_datetime <= datetime.now():
        await message.answer(
            "❌ Дата должна быть в будущем!\n\n"
            "Введите корректную дату."
        )
        return

    # Сохраняем дату в FSM storage
    await state.update_data(event_datetime=event_datetime)

    # Переходим к следующему шагу - стоимость
    await message.answer(messages.ADMIN_WEBINAR_PRICE)
    await state.set_state(AdminWebinarStates.waiting_for_price)


@router.message(AdminWebinarStates.waiting_for_price)
async def process_webinar_price(message: Message, state: FSMContext):
    """
    Обработка стоимости вебинара
    """
    price_str = message.text.strip()

    logger.info(f"Получена стоимость: {price_str}")

    # Валидация стоимости
    price = validators.validate_price(price_str)

    if price is None:
        await message.answer(messages.ADMIN_INVALID_PRICE)
        return

    if price < 0:
        await message.answer("❌ Стоимость не может быть отрицательной!")
        return

    # Сохраняем стоимость в FSM storage
    await state.update_data(price=float(price))

    # Переходим к следующему шагу - место проведения
    await message.answer(messages.ADMIN_WEBINAR_LOCATION)
    await state.set_state(AdminWebinarStates.waiting_for_location)


@router.message(AdminWebinarStates.waiting_for_location)
async def process_webinar_location(message: Message, state: FSMContext):
    """
    Обработка места проведения / ссылки
    """
    location = message.text.strip()

    logger.info(f"Получено место: {location}")

    # Валидация
    if len(location) > 500:
        await message.answer("❌ Слишком длинный текст! Максимум 500 символов.")
        return

    # Сохраняем место в FSM storage
    await state.update_data(location=location)

    # Переходим к последнему шагу - ссылка на оплату
    await message.answer(messages.ADMIN_WEBINAR_PAYMENT_LINK)
    await state.set_state(AdminWebinarStates.waiting_for_payment_link)


@router.message(AdminWebinarStates.waiting_for_payment_link)
async def process_webinar_payment_link(message: Message, state: FSMContext):
    """
    Обработка ссылки на оплату (опционально)
    """
    payment_link_str = message.text.strip()

    logger.info(f"Получена ссылка на оплату: {payment_link_str}")

    payment_link = None

    # Проверка на команды пропуска или автоматическую генерацию
    if payment_link_str.lower() in ["/skip", "/auto"]:
        payment_link = None
        logger.info("Ссылка на оплату пропущена, будет использоваться ЮKassa")
    else:
        # Валидация URL
        if not validators.validate_url(payment_link_str):
            await message.answer(
                "❌ Некорректная ссылка!\n\n"
                "Введите корректный URL или отправьте /skip"
            )
            return
        payment_link = payment_link_str

    # Сохраняем ссылку в FSM storage
    await state.update_data(payment_link=payment_link)

    # Получаем все данные из FSM storage
    data = await state.get_data()

    # Создаем вебинар в БД
    async with async_session_maker() as session:
        try:
            webinar = await crud.create_webinar(
                session=session,
                title=data['title'],
                description=data.get('description'),
                event_datetime=data['event_datetime'],
                price=Decimal(data['price']),
                location=data['location'],
                payment_link=data.get('payment_link')
            )

            logger.info(f"Вебинар создан: ID={webinar.id}, title={webinar.title}")

            # Сбрасываем состояние FSM
            await state.clear()

            # Форматируем дату для отображения
            date_str = webinar.event_datetime.strftime("%d.%m.%Y %H:%M")

            # Отправляем подтверждение
            await message.answer(
                messages.ADMIN_WEBINAR_CREATED.format(
                    title=webinar.title,
                    date=date_str,
                    price=f"{webinar.price:.0f}"
                )
            )

        except Exception as e:
            logger.error(f"Ошибка при создании вебинара: {e}", exc_info=True)
            await message.answer(messages.ERROR_GENERIC)


@router.callback_query(F.data == "admin_view_stats")
async def callback_view_stats(callback: CallbackQuery):
    """
    Показать статистику
    """
    logger.info(f"Администратор {callback.from_user.id} запросил статистику")

    async with async_session_maker() as session:
        try:
            # Получаем статистику
            total_users = await crud.get_users_count(session)
            total_webinars = await crud.get_webinars_count(session)
            total_purchases = await crud.get_purchases_count(session)

            # Получаем активный вебинар
            active_webinar = await crud.get_active_webinar(session)

            if active_webinar:
                webinar_purchases = await crud.get_webinar_purchases_count(
                    session,
                    active_webinar.id
                )
                active_webinar_info = f"""
📊 **Активный вебинар:**
🎓 {active_webinar.title}
📅 {active_webinar.event_datetime.strftime("%d.%m.%Y %H:%M")}
👥 Участников: {webinar_purchases}
"""
            else:
                active_webinar_info = "\n📊 **Активный вебинар:** Нет"

            # Формируем сообщение со статистикой
            stats_message = f"""📈 **Статистика бота**

👥 **Всего пользователей:** {total_users}
🎓 **Всего вебинаров:** {total_webinars}
💳 **Всего покупок:** {total_purchases}
{active_webinar_info}
"""

            await callback.message.answer(stats_message)
            await callback.answer()

        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}", exc_info=True)
            await callback.answer("❌ Ошибка при получении статистики!", show_alert=True)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """
    Команда /stats - показать статистику
    """
    # Перенаправляем на callback обработчик
    # Создаем фейковый callback
    from aiogram.types import CallbackQuery as CQ
    from unittest.mock import AsyncMock

    # Используем упрощенный вариант - просто копируем логику
    async with async_session_maker() as session:
        try:
            total_users = await crud.get_users_count(session)
            total_webinars = await crud.get_webinars_count(session)
            total_purchases = await crud.get_purchases_count(session)

            active_webinar = await crud.get_active_webinar(session)

            if active_webinar:
                webinar_purchases = await crud.get_webinar_purchases_count(
                    session,
                    active_webinar.id
                )
                active_webinar_info = f"""
📊 **Активный вебинар:**
🎓 {active_webinar.title}
📅 {active_webinar.event_datetime.strftime("%d.%m.%Y %H:%M")}
👥 Участников: {webinar_purchases}
"""
            else:
                active_webinar_info = "\n📊 **Активный вебинар:** Нет"

            stats_message = f"""📈 **Статистика бота**

👥 **Всего пользователей:** {total_users}
🎓 **Всего вебинаров:** {total_webinars}
💳 **Всего покупок:** {total_purchases}
{active_webinar_info}
"""

            await message.answer(stats_message)

        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}", exc_info=True)
            await message.answer(messages.ERROR_GENERIC)
