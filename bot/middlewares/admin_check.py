"""
Middleware для проверки прав администратора

Используется для защиты админских команд.
Проверяет, что пользователь находится в списке администраторов.
"""

import logging
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.config import settings
from bot.texts import messages

logger = logging.getLogger(__name__)


class AdminCheckMiddleware(BaseMiddleware):
    """
    Middleware для проверки прав администратора

    Блокирует выполнение handler'а если пользователь не является администратором
    """

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """
        Проверка прав администратора

        Args:
            handler: Следующий обработчик в цепочке
            event: Message или CallbackQuery
            data: Дополнительные данные

        Returns:
            Результат выполнения handler'а или None если нет прав
        """
        user_id = event.from_user.id

        # Проверяем является ли пользователь администратором
        if not settings.is_admin(user_id):
            logger.warning(f"Попытка доступа к админ-функциям от пользователя {user_id}")

            # Отправляем сообщение об отказе
            if isinstance(event, Message):
                await event.answer(messages.NOT_ADMIN)
            elif isinstance(event, CallbackQuery):
                await event.answer(messages.NOT_ADMIN, show_alert=True)

            # Блокируем выполнение handler'а
            return

        # Пользователь является администратором - продолжаем выполнение
        logger.debug(f"Администратор {user_id} получил доступ")

        # Добавляем флаг is_admin в data для использования в handler'ах
        data["is_admin"] = True

        return await handler(event, data)
