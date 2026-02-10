"""
Handler для вебинаров

Обрабатывает:
- Команду/сообщение "Вебинар" - показ списка всех активных вебинаров
- Callback выбора конкретного вебинара
- Проверку покупки и отправку ссылки на группу
"""

import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.db_setup import async_session_maker
from bot.database import crud
from bot.utils.keyboards import get_webinars_list_keyboard
from bot.texts import messages

logger = logging.getLogger(__name__)

# Создаем router для этого модуля
router = Router(name='webinar')


@router.message(F.text == messages.BUTTON_WEBINAR)
@router.message(F.text.lower().in_(['вебинар', 'вебинары', 'webinar']))
async def cmd_webinar(message: Message):
    """
    Обработка команды "Вебинар"

    Показывает список всех активных вебинаров
    """
    user_id = message.from_user.id

    logger.info(f"Команда 'Вебинар' от пользователя {user_id}")

    async with async_session_maker() as session:
        # Получаем все активные вебинары
        webinars = await crud.get_all_active_webinars(session)

        if not webinars:
            # Нет активных вебинаров
            logger.info("Нет активных вебинаров")
            await message.answer(messages.NO_ACTIVE_WEBINAR)
            return

        logger.info(f"Найдено {len(webinars)} активных вебинаров")

        # Отправляем список вебинаров с inline кнопками
        await message.answer(
            "🎓 **Доступные вебинары:**\n\n"
            "Выберите вебинар, чтобы узнать подробности:",
            reply_markup=get_webinars_list_keyboard(webinars)
        )


@router.callback_query(F.data.startswith("select_webinar_"))
async def callback_select_webinar(callback: CallbackQuery):
    """
    Обработка выбора конкретного вебинара

    Callback data: select_webinar_{webinar_id}

    Логика:
    1. Проверить, купил ли пользователь этот вебинар
    2. Если купил → показать ссылку на группу
    3. Если не купил → показать информацию и кнопку оплаты
    """
    try:
        user_id = callback.from_user.id

        # Извлекаем webinar_id из callback_data
        webinar_id = int(callback.data.split("_")[2])

        logger.info(f"Пользователь {user_id} выбрал вебинар {webinar_id}")

        async with async_session_maker() as session:
            # Получаем вебинар
            webinar = await crud.get_webinar_by_id(session, webinar_id)

            if not webinar:
                await callback.answer("❌ Вебинар не найден!", show_alert=True)
                return

            # Проверяем, купил ли пользователь этот вебинар
            purchase = await crud.get_user_purchase_for_webinar(
                session,
                user_id,
                webinar_id
            )

            # Форматируем дату и время
            date_str = webinar.event_datetime.strftime("%d.%m.%Y")
            time_str = webinar.event_datetime.strftime("%H:%M")

            if purchase and purchase.payment_status == 'succeeded':
                # ✅ ВЕБИНАР КУПЛЕН - показываем ссылку на группу
                logger.info(f"Пользователь {user_id} уже купил вебинар {webinar_id}")

                if webinar.group_link:
                    # Есть ссылка на группу
                    message_text = f"""✅ **У вас есть доступ к вебинару!**

🎓 **{webinar.title}**
📅 Дата: {date_str}
🕐 Время: {time_str}

🔗 **Ссылка для вступления в группу:**
{webinar.group_link}

⏰ Напоминания:
• За 24 часа до начала
• За 1 час до начала

До встречи на вебинаре! 🚀"""

                    # Создаем кнопку со ссылкой на группу
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="👥 Перейти в группу",
                            url=webinar.group_link
                        )]
                    ])

                    await callback.message.answer(message_text, reply_markup=keyboard)
                else:
                    # Нет ссылки на группу
                    message_text = f"""✅ **У вас есть доступ к вебинару!**

🎓 **{webinar.title}**
📅 Дата: {date_str}
🕐 Время: {time_str}
📍 {webinar.location or "Онлайн"}

⏰ Вы получите напоминания:
• За 24 часа до начала
• За 1 час до начала

Ссылка на вебинар будет отправлена за 1 час до начала."""

                    await callback.message.answer(message_text)

                await callback.answer()

            else:
                # ❌ ВЕБИНАР НЕ КУПЛЕН - показываем информацию и кнопку оплаты
                logger.info(f"Пользователь {user_id} не купил вебинар {webinar_id}, показываем информацию")

                # Форматируем цену
                price_str = f"{webinar.price:.0f}" if webinar.price else "Бесплатно"

                # Формируем сообщение с информацией
                webinar_info = messages.WEBINAR_INFO.format(
                    title=webinar.title,
                    description=webinar.description or "Подробная информация будет позже",
                    date=date_str,
                    time=time_str,
                    location=webinar.location or "Онлайн",
                    price=price_str
                )

                # Проверяем наличие готовой ссылки на оплату
                if webinar.payment_link:
                    # Есть готовая ссылка на оплату (созданная вручную)
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text=messages.BUTTON_PAY,
                            url=webinar.payment_link
                        )]
                    ])
                    await callback.message.answer(webinar_info, reply_markup=keyboard)
                else:
                    # Нет ссылки - используем автоматическую генерацию через ЮKassa
                    logger.info(f"У вебинара {webinar_id} нет payment_link, создаем через ЮKassa")

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text=messages.BUTTON_PAY,
                            callback_data=f"create_payment_{webinar.id}"
                        )]
                    ])

                    await callback.message.answer(webinar_info, reply_markup=keyboard)

                await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при обработке выбора вебинара: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка!", show_alert=True)
