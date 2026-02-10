"""
Handler для FAQ и поддержки

Обрабатывает:
- Команду /help и кнопку "Помощь"
- FAQ меню с вопросами
- Задавание вопросов в поддержку
- Отправку вопросов в супергруппу
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.database.db_setup import async_session_maker
from bot.database import crud
from bot.states.support import SupportStates
from bot.utils.keyboards import get_faq_keyboard, get_main_menu_keyboard
from bot.texts import messages
from bot.texts.faq import get_faq_questions, get_faq_answer
from bot.config import settings

logger = logging.getLogger(__name__)

# Создаем router для этого модуля
router = Router(name='support')


@router.message(Command("help"))
@router.message(F.text == messages.BUTTON_HELP)
async def cmd_help(message: Message):
    """
    Обработка команды /help и кнопки "Помощь"

    Показывает FAQ меню с вопросами
    """
    user_id = message.from_user.id

    logger.info(f"Команда /help от пользователя {user_id}")

    # Получаем список FAQ вопросов
    faq_questions = get_faq_questions()

    # Отправляем меню с FAQ
    await message.answer(
        messages.HELP_MESSAGE,
        reply_markup=get_faq_keyboard(faq_questions)
    )


@router.callback_query(F.data.startswith("faq_"))
async def callback_faq_question(callback: CallbackQuery):
    """
    Обработка нажатия на FAQ вопрос

    Callback data: faq_{index}
    """
    try:
        # Извлекаем индекс вопроса
        question_index = int(callback.data.split("_")[1])

        logger.info(f"Пользователь {callback.from_user.id} выбрал FAQ вопрос {question_index}")

        # Получаем ответ на вопрос
        answer = get_faq_answer(question_index)

        # Отправляем ответ
        await callback.message.answer(answer)

        await callback.answer()

    except (IndexError, ValueError) as e:
        logger.error(f"Ошибка при обработке FAQ вопроса: {e}")
        await callback.answer("❌ Вопрос не найден!", show_alert=True)


@router.callback_query(F.data == "ask_custom_question")
async def callback_ask_custom_question(callback: CallbackQuery, state: FSMContext):
    """
    Обработка нажатия на кнопку "Задать свой вопрос"

    Запускает FSM для получения вопроса от пользователя
    """
    logger.info(f"Пользователь {callback.from_user.id} хочет задать свой вопрос")

    # Отправляем инструкцию
    await callback.message.answer(messages.FAQ_NO_ANSWER)

    # Устанавливаем состояние FSM
    await state.set_state(SupportStates.waiting_for_question)

    await callback.answer()


@router.message(SupportStates.waiting_for_question)
async def process_support_question(message: Message, state: FSMContext):
    """
    Обработка вопроса от пользователя

    Сохраняет вопрос в БД и отправляет в супергруппу
    """
    user_id = message.from_user.id
    question = message.text.strip()

    logger.info(f"Получен вопрос от пользователя {user_id}: {question[:50]}...")

    # Проверяем длину вопроса
    if len(question) < 10:
        await message.answer(
            "❌ Вопрос слишком короткий!\n\n"
            "Пожалуйста, опишите вашу проблему подробнее (минимум 10 символов)."
        )
        return

    if len(question) > 1000:
        await message.answer(
            "❌ Вопрос слишком длинный!\n\n"
            "Пожалуйста, сократите ваш вопрос (максимум 1000 символов)."
        )
        return

    async with async_session_maker() as session:
        try:
            # Получаем пользователя из БД
            user = await crud.get_user_by_telegram_id(session, user_id)

            if not user:
                logger.error(f"Пользователь {user_id} не найден в БД")
                await message.answer(messages.ERROR_GENERIC)
                return

            # Сохраняем вопрос в БД
            ticket = await crud.create_support_ticket(
                session=session,
                user_id=user.id,
                question=question
            )

            logger.info(f"Создан тикет в поддержку: ID={ticket.id}")

            # Формируем сообщение для отправки в супергруппу
            support_message = f"""🆘 **Новый вопрос в поддержку**

👤 **От:** {message.from_user.first_name or 'Пользователь'}
📧 **Email:** {user.email}
🆔 **User ID:** {user_id}
🎫 **Ticket ID:** {ticket.id}

❓ **Вопрос:**
{question}

---
_Для ответа используйте:_ `/reply {user_id} <ответ>`"""

            # Отправляем вопрос в супергруппу
            try:
                if settings.support_group_id and settings.support_topic_id:
                    await message.bot.send_message(
                        chat_id=settings.support_group_id,
                        text=support_message,
                        message_thread_id=settings.support_topic_id
                    )
                    logger.info(f"Вопрос отправлен в супергруппу (topic {settings.support_topic_id})")
                elif settings.support_group_id:
                    # Если нет topic_id - отправляем просто в группу
                    await message.bot.send_message(
                        chat_id=settings.support_group_id,
                        text=support_message
                    )
                    logger.info("Вопрос отправлен в супергруппу")
                else:
                    logger.warning("SUPPORT_GROUP_ID не настроен, вопрос не отправлен")

            except Exception as e:
                logger.error(f"Ошибка при отправке в супергруппу: {e}", exc_info=True)
                # Продолжаем выполнение, даже если не удалось отправить в группу

            # Сбрасываем состояние FSM
            await state.clear()

            # Отправляем подтверждение пользователю
            await message.answer(
                messages.SUPPORT_QUESTION_RECEIVED,
                reply_markup=get_main_menu_keyboard()
            )

        except Exception as e:
            logger.error(f"Ошибка при обработке вопроса: {e}", exc_info=True)
            await message.answer(messages.ERROR_GENERIC)


@router.message(F.text.lower().in_(['помощь', 'поддержка', 'help', 'support', 'faq']))
async def cmd_help_text(message: Message):
    """
    Обработка текстовых вариантов команды help

    Перенаправляем на основной обработчик
    """
    await cmd_help(message)
