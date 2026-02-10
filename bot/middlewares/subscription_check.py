"""
Middleware для проверки подписки на канал

Проверяет подписку пользователя перед каждым обращением к боту
"""

import logging
from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.config import settings
from bot.services.subscription_service import check_user_subscription, get_channel_link
from bot.utils.keyboards import get_subscription_check_keyboard
from bot.texts import messages

logger = logging.getLogger(__name__)


class SubscriptionCheckMiddleware(BaseMiddleware):
    """
    Middleware для проверки подписки на канал

    Пропускает только команду /start и callback для проверки подписки
    Остальные команды требуют подписки
    """

    # Список команд, которые доступны без подписки
    ALLOWED_WITHOUT_SUBSCRIPTION = [
        '/start',
        'check_subscription',  # callback для проверки подписки
    ]

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """
        Основная функция middleware

        Args:
            handler: Следующий обработчик
            event: Событие (Message или CallbackQuery)
            data: Данные контекста
        """

        # Получаем user_id
        user_id = event.from_user.id

        # Определяем, это Message или CallbackQuery
        if isinstance(event, Message):
            # Для сообщений проверяем команду
            command_text = event.text

            # Команда /start всегда доступна
            if command_text and command_text.startswith('/start'):
                return await handler(event, data)

        elif isinstance(event, CallbackQuery):
            # Для callback проверяем callback_data
            callback_data = event.data

            # Callback проверки подписки всегда доступен
            if callback_data == 'check_subscription':
                return await handler(event, data)

        # Проверяем подписку на канал
        is_subscribed = await check_user_subscription(
            bot=data['bot'],
            user_id=user_id,
            channel_id=settings.channel_id
        )

        if is_subscribed:
            # Пользователь подписан - пропускаем дальше
            logger.info(f"Пользователь {user_id} подписан, обработка продолжается")
            return await handler(event, data)

        # Пользователь НЕ подписан - отправляем сообщение
        logger.warning(f"Пользователь {user_id} НЕ подписан на канал")

        # Получаем ссылку на канал
        channel_link = await get_channel_link(data['bot'], settings.channel_id)

        # Формируем клавиатуру
        keyboard = get_subscription_check_keyboard(channel_link)

        # Отправляем сообщение
        message_text = messages.NOT_SUBSCRIBED.format(
            channel_link=channel_link or "Канал (обратитесь к администратору)"
        )

        if isinstance(event, Message):
            await event.answer(
                message_text,
                reply_markup=keyboard
            )
        elif isinstance(event, CallbackQuery):
            await event.message.answer(
                message_text,
                reply_markup=keyboard
            )
            # Отвечаем на callback, чтобы убрать "часики"
            await event.answer("Сначала подпишитесь на канал", show_alert=True)

        # Останавливаем обработку - не пропускаем дальше
        return
