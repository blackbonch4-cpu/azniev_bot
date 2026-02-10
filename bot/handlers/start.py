"""
Handler для команды /start и регистрации пользователя

Обрабатывает:
- Команду /start
- Процесс регистрации (запрос email)
- Callback проверки подписки
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.database.db_setup import async_session_maker
from bot.database import crud
from bot.states.registration import RegistrationStates
from bot.utils import validators
from bot.utils.keyboards import get_main_menu_keyboard, get_subscription_check_keyboard
from bot.texts import messages
from bot.config import settings
from bot.services.subscription_service import check_user_subscription, get_channel_link
from bot.services import sheets_service

logger = logging.getLogger(__name__)

# Создаем router для этого модуля
router = Router(name='start')


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработка команды /start

    Логика:
    1. Проверить подписку (middleware уже проверил)
    2. Проверить регистрацию в БД
    3. Если не зарегистрирован - запустить процесс регистрации
    4. Если зарегистрирован - показать главное меню
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Пользователь"

    logger.info(f"Команда /start от пользователя {user_id}")

    # Получаем сессию БД
    async with async_session_maker() as session:
        # Проверяем регистрацию в БД
        user = await crud.get_user_by_telegram_id(session, user_id)

        if user:
            # Пользователь уже зарегистрирован
            logger.info(f"Пользователь {user_id} уже зарегистрирован")

            # Обновляем время последнего взаимодействия
            await crud.update_user_last_interaction(session, user_id)

            # Показываем главное меню
            await message.answer(
                messages.MAIN_MENU.format(first_name=first_name),
                reply_markup=get_main_menu_keyboard()
            )

        else:
            # Пользователь не зарегистрирован - начинаем регистрацию
            logger.info(f"Новый пользователь {user_id}, начинаем регистрацию")

            # Отправляем приветствие
            await message.answer(
                messages.WELCOME_NEW_USER.format(first_name=first_name)
            )

            # Запрашиваем email
            await message.answer(messages.REQUEST_EMAIL)

            # Устанавливаем состояние FSM - ожидание email
            await state.set_state(RegistrationStates.waiting_for_email)


@router.message(RegistrationStates.waiting_for_email)
async def process_email_registration(message: Message, state: FSMContext):
    """
    Обработка ввода email при регистрации

    Проверяет email и сохраняет пользователя в БД
    """
    user_id = message.from_user.id
    email = message.text.strip()

    logger.info(f"Получен email от пользователя {user_id}: {email}")

    # Валидация email
    if not validators.validate_email(email):
        logger.warning(f"Некорректный email: {email}")
        await message.answer(messages.INVALID_EMAIL)
        return

    # Email корректен - сохраняем пользователя
    async with async_session_maker() as session:
        try:
            # Проверяем что такой email еще не используется
            existing_user = await crud.get_user_by_email(session, email)

            if existing_user:
                logger.warning(f"Email {email} уже зарегистрирован")
                await message.answer(
                    "❌ Этот email уже используется другим пользователем. Пожалуйста, укажите другой email."
                )
                return

            # Создаем пользователя
            user = await crud.create_user(
                session=session,
                telegram_id=user_id,
                email=email,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                username=message.from_user.username,
            )

            logger.info(f"Пользователь {user_id} успешно зарегистрирован с email {email}")

            # Сбрасываем состояние FSM
            await state.clear()

            # Отправляем сообщение об успешной регистрации
            await message.answer(
                messages.REGISTRATION_SUCCESS,
                reply_markup=get_main_menu_keyboard()
            )

            # Синхронизация с Google Sheets
            await sheets_service.add_user_to_sheets(
                user_id=user.id,
                telegram_id=user.telegram_id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                email=user.email,
                registration_date=user.registration_date,
                is_subscribed=user.is_subscribed
            )

            # Показываем доступные вебинары сразу после регистрации
            from bot.utils.keyboards import get_webinars_list_keyboard
            webinars = await crud.get_all_active_webinars(session)

            if webinars:
                await message.answer(
                    "🎓 **Доступные вебинары:**\n\n"
                    "Выберите вебинар, чтобы узнать подробности:",
                    reply_markup=get_webinars_list_keyboard(webinars)
                )

        except Exception as e:
            logger.error(f"Ошибка при регистрации пользователя: {e}")
            await message.answer(messages.ERROR_GENERIC)


@router.callback_query(F.data == "check_subscription")
async def callback_check_subscription(callback: CallbackQuery):
    """
    Обработка callback кнопки "Проверить подписку"

    Проверяет подписку и отправляет результат
    """
    user_id = callback.from_user.id

    logger.info(f"Проверка подписки для пользователя {user_id}")

    # Проверяем подписку
    is_subscribed = await check_user_subscription(
        bot=callback.bot,
        user_id=user_id,
        channel_id=settings.channel_id
    )

    if is_subscribed:
        # Пользователь подписан
        logger.info(f"Пользователь {user_id} успешно подписался")

        # Обновляем статус подписки в БД (если пользователь уже зарегистрирован)
        async with async_session_maker() as session:
            user = await crud.get_user_by_telegram_id(session, user_id)
            if user:
                await crud.update_user_subscription(session, user_id, True)

        # Отправляем сообщение
        await callback.message.answer(
            "✅ Отлично! Вы подписаны на канал.\n\n"
            "Теперь вы можете продолжить работу с ботом."
        )

        # Удаляем предыдущее сообщение с кнопкой
        await callback.message.delete()

        # Отправляем приветствие или главное меню
        # Проверяем регистрацию
        async with async_session_maker() as session:
            user = await crud.get_user_by_telegram_id(session, user_id)

            if user:
                # Зарегистрирован - показываем меню
                await callback.message.answer(
                    messages.MAIN_MENU.format(first_name=callback.from_user.first_name),
                    reply_markup=get_main_menu_keyboard()
                )
            else:
                # Не зарегистрирован - запускаем регистрацию
                await callback.message.answer(
                    messages.WELCOME_NEW_USER.format(first_name=callback.from_user.first_name)
                )
                await callback.message.answer(messages.REQUEST_EMAIL)

                # Устанавливаем состояние FSM через callback нельзя напрямую
                # Нужен state из контекста, поэтому просто отправляем сообщение
                # Пользователь должен будет написать email, и это обработается в следующем хэндлере

    else:
        # Пользователь все еще не подписан
        logger.warning(f"Пользователь {user_id} все еще не подписан")

        # Получаем ссылку на канал
        channel_link = await get_channel_link(callback.bot, settings.channel_id)

        await callback.answer(
            "❌ Вы все еще не подписаны на канал. Пожалуйста, подпишитесь и попробуйте снова.",
            show_alert=True
        )

        # Отправляем сообщение снова
        await callback.message.answer(
            messages.NOT_SUBSCRIBED.format(
                channel_link=channel_link or "Канал (обратитесь к администратору)"
            ),
            reply_markup=get_subscription_check_keyboard(channel_link)
        )
