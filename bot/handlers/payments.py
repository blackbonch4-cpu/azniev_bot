"""
Handler для обработки платежей

Обрабатывает:
- Создание платежа через ЮKassa
- Проверку статуса платежа
- Обновление статуса в БД
- Уведомление пользователя об успешной оплате
"""

import logging
from decimal import Decimal
from typing import Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.db_setup import async_session_maker
from bot.database import crud
from bot.services import payment_service, sheets_service
from bot.texts import messages
from bot.utils.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)

# Создаем router для этого модуля
router = Router(name='payments')


async def create_payment_for_webinar(
    user_id: int,
    webinar_id: int,
    webinar_title: str,
    price: Decimal
) -> Optional[dict]:
    """
    Создать платеж для вебинара

    Args:
        user_id: Telegram ID пользователя
        webinar_id: ID вебинара
        webinar_title: Название вебинара
        price: Стоимость

    Returns:
        dict с данными платежа или None
    """
    try:
        # Создаем платеж через ЮKassa
        payment_data = payment_service.create_payment(
            amount=price,
            description=f"Оплата вебинара: {webinar_title}",
            metadata={
                "user_id": user_id,
                "webinar_id": webinar_id
            }
        )

        if not payment_data:
            logger.error(f"Не удалось создать платеж для пользователя {user_id}")
            return None

        logger.info(f"Платеж создан: {payment_data['id']}")

        # Сохраняем покупку в БД со статусом pending
        async with async_session_maker() as session:
            # Получаем user из БД
            user = await crud.get_user_by_telegram_id(session, user_id)

            if not user:
                logger.error(f"Пользователь {user_id} не найден в БД")
                return None

            # Создаем запись о покупке
            purchase = await crud.create_purchase(
                session=session,
                user_id=user.id,  # DB ID, не telegram_id!
                webinar_id=webinar_id,
                payment_id=payment_data['id'],
                payment_status='pending'
            )

            logger.info(f"Покупка создана: Purchase ID={purchase.id}, Payment ID={payment_data['id']}")

        return payment_data

    except Exception as e:
        logger.error(f"Ошибка при создании платежа: {e}", exc_info=True)
        return None


@router.callback_query(F.data.startswith("create_payment_"))
async def callback_create_payment(callback: CallbackQuery):
    """
    Создать платеж для вебинара

    Callback data: create_payment_{webinar_id}
    """
    try:
        user_id = callback.from_user.id

        # Извлекаем webinar_id из callback_data
        webinar_id = int(callback.data.split("_")[2])

        logger.info(f"Создание платежа для пользователя {user_id}, вебинар {webinar_id}")

        async with async_session_maker() as session:
            # Получаем вебинар
            webinar = await crud.get_webinar_by_id(session, webinar_id)

            if not webinar:
                await callback.answer("❌ Вебинар не найден!", show_alert=True)
                return

            # Проверяем, что пользователь еще не купил билет
            purchase = await crud.get_user_purchase_for_webinar(session, user_id, webinar_id)

            if purchase and purchase.payment_status == 'succeeded':
                await callback.answer("✅ Вы уже приобрели билет на этот вебинар!", show_alert=True)
                return

        # Создаем платеж
        payment_data = await create_payment_for_webinar(
            user_id=user_id,
            webinar_id=webinar.id,
            webinar_title=webinar.title,
            price=Decimal(webinar.price)
        )

        if not payment_data:
            await callback.answer("❌ Ошибка при создании платежа. Попробуйте позже.", show_alert=True)
            return

        # Отправляем ссылку на оплату
        payment_message = payment_service.format_payment_link_message(
            webinar_title=webinar.title,
            price=Decimal(webinar.price),
            confirmation_url=payment_data['confirmation_url']
        )

        # Создаем клавиатуру с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="💳 Перейти к оплате",
                url=payment_data['confirmation_url']
            )],
            [InlineKeyboardButton(
                text="✅ Я оплатил, проверить",
                callback_data=f"check_payment_{payment_data['id']}"
            )]
        ])

        await callback.message.answer(payment_message, reply_markup=keyboard)
        await callback.answer("✅ Платеж создан!")

    except Exception as e:
        logger.error(f"Ошибка в callback_create_payment: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка!", show_alert=True)


@router.callback_query(F.data.startswith("check_payment_"))
async def callback_check_payment(callback: CallbackQuery):
    """
    Проверить статус платежа

    Callback data: check_payment_{payment_id}
    """
    try:
        user_id = callback.from_user.id

        # Извлекаем payment_id из callback_data
        payment_id = callback.data.split("check_payment_")[1]

        logger.info(f"Проверка платежа {payment_id} для пользователя {user_id}")

        # Получаем статус платежа из ЮKassa
        payment_status_data = payment_service.get_payment_status(payment_id)

        if not payment_status_data:
            await callback.answer("❌ Ошибка при проверке платежа. Попробуйте позже.", show_alert=True)
            return

        payment_status = payment_status_data['status']

        logger.info(f"Статус платежа {payment_id}: {payment_status}")

        # Обновляем статус в БД
        async with async_session_maker() as session:
            # Находим покупку по payment_id
            purchase = await crud.get_purchase_by_payment_id(session, payment_id)

            if not purchase:
                await callback.answer("❌ Покупка не найдена!", show_alert=True)
                return

            # Проверяем, что это покупка текущего пользователя
            if purchase.user.telegram_id != user_id:
                await callback.answer("❌ Это не ваша покупка!", show_alert=True)
                return

            if payment_status == 'succeeded':
                # Платеж успешен
                logger.info(f"Платеж {payment_id} успешно оплачен")

                # Обновляем статус в БД
                await crud.update_purchase_status(session, payment_id, 'succeeded')

                # Получаем информацию о вебинаре
                webinar = purchase.webinar
                date_str = webinar.event_datetime.strftime("%d.%m.%Y")
                time_str = webinar.event_datetime.strftime("%H:%M")

                # Отправляем поздравление
                success_message = messages.PAYMENT_SUCCESS.format(
                    title=webinar.title,
                    date=date_str,
                    time=time_str,
                    location=webinar.location or "Онлайн"
                )

                await callback.message.answer(
                    success_message,
                    reply_markup=get_main_menu_keyboard()
                )

                await callback.answer("🎉 Оплата успешна!", show_alert=True)

                # Синхронизация с Google Sheets
                await sheets_service.add_purchase_to_sheets(
                    purchase_id=purchase.id,
                    telegram_id=purchase.user.telegram_id,
                    user_name=f"{purchase.user.first_name or ''} {purchase.user.last_name or ''}".strip(),
                    email=purchase.user.email,
                    webinar_title=webinar.title,
                    webinar_date=webinar.event_datetime,
                    price=float(webinar.price),
                    payment_status=payment_status,
                    purchase_date=purchase.purchase_date
                )

            elif payment_status == 'pending':
                # Платеж еще не оплачен
                await callback.answer(
                    "⏳ Платеж еще не оплачен.\n\n"
                    "Пожалуйста, завершите оплату и попробуйте снова.",
                    show_alert=True
                )

            elif payment_status == 'canceled':
                # Платеж отменен
                await crud.update_purchase_status(session, payment_id, 'canceled')
                await callback.answer("❌ Платеж был отменен.", show_alert=True)

            else:
                # Неизвестный статус
                await callback.answer(f"⚠️ Статус платежа: {payment_status}", show_alert=True)

    except Exception as e:
        logger.error(f"Ошибка в callback_check_payment: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка при проверке платежа!", show_alert=True)
