"""
Сервис для проверки подписки пользователя на канал

Проверяет, подписан ли пользователь на указанный канал/группу
"""

import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


async def check_user_subscription(bot: Bot, user_id: int, channel_id: int) -> bool:
    """
    Проверка подписки пользователя на канал

    Args:
        bot: Экземпляр бота
        user_id: Telegram ID пользователя
        channel_id: ID канала/группы (начинается с -100)

    Returns:
        True если пользователь подписан, False если нет
    """
    try:
        # Получаем информацию о участнике чата
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)

        logger.info(f"Статус пользователя {user_id} в канале {channel_id}: {member.status}")

        # Проверяем статус участника
        # Возможные статусы: creator, administrator, member, restricted, left, kicked
        if member.status in ['creator', 'administrator', 'member']:
            logger.info(f"Пользователь {user_id} подписан на канал {channel_id}")
            return True

        # Пользователь с ограничениями может быть участником группы
        if member.status == 'restricted' and getattr(member, 'is_member', False):
            logger.info(f"Пользователь {user_id} подписан на канал {channel_id} (restricted, но is_member=True)")
            return True

        logger.info(f"Пользователь {user_id} НЕ подписан на канал {channel_id}. Статус: {member.status}")
        return False

    except TelegramBadRequest as e:
        # Возможные ошибки:
        # - User not found (пользователь не найден в канале)
        # - Chat not found (канал не найден)
        # - Bot is not a member (бот не добавлен в канал)
        logger.error(f"Ошибка при проверке подписки (user={user_id}, channel={channel_id}): {e}")
        return False

    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке подписки (user={user_id}, channel={channel_id}): {e}", exc_info=True)
        return False


async def get_channel_link(bot: Bot, channel_id: int) -> Optional[str]:
    """
    Получить ссылку на канал

    Args:
        bot: Экземпляр бота
        channel_id: ID канала

    Returns:
        Ссылка на канал или None
    """
    try:
        chat = await bot.get_chat(channel_id)

        # Если у канала есть username (публичный)
        if chat.username:
            return f"https://t.me/{chat.username}"

        # Для приватных каналов можно попробовать получить invite link
        # Но для этого бот должен иметь права администратора с возможностью создания ссылок
        try:
            invite_link = await bot.export_chat_invite_link(channel_id)
            return invite_link
        except:
            pass

        return None

    except Exception as e:
        logger.error(f"Ошибка при получении ссылки на канал: {e}")
        return None
