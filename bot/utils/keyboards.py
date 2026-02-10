"""
Клавиатуры для Telegram бота

Все inline и reply клавиатуры
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot.texts import messages


# ===== REPLY KEYBOARDS =====

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота (Reply Keyboard)"""
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text=messages.BUTTON_WEBINAR))
    builder.add(KeyboardButton(text=messages.BUTTON_HELP))

    builder.adjust(2)  # 2 кнопки в ряд

    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


# ===== INLINE KEYBOARDS =====

def get_subscription_check_keyboard(channel_link: str = None) -> InlineKeyboardMarkup:
    """
    Клавиатура для проверки подписки на канал

    Args:
        channel_link: Ссылка на канал (опционально)
    """
    builder = InlineKeyboardBuilder()

    # Если есть ссылка на канал - добавляем кнопку перехода
    if channel_link:
        builder.add(
            InlineKeyboardButton(
                text="📢 Перейти в канал",
                url=channel_link
            )
        )

    # Кнопка проверки подписки
    builder.add(
        InlineKeyboardButton(
            text=messages.BUTTON_CHECK_SUBSCRIPTION,
            callback_data="check_subscription"
        )
    )

    builder.adjust(1)  # По 1 кнопке в ряд

    return builder.as_markup()


def get_payment_keyboard(payment_link: str) -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопкой оплаты

    Args:
        payment_link: Ссылка на оплату
    """
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text=messages.BUTTON_PAY,
            url=payment_link
        )
    )

    return builder.as_markup()


def get_faq_keyboard(questions: list[str]) -> InlineKeyboardMarkup:
    """
    Клавиатура с FAQ вопросами

    Args:
        questions: Список вопросов
    """
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки для каждого вопроса
    for i, question in enumerate(questions):
        # Обрезаем длинные вопросы для кнопки
        button_text = question if len(question) <= 50 else question[:47] + "..."

        builder.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"faq_{i}"
            )
        )

    # Кнопка "Задать свой вопрос"
    builder.add(
        InlineKeyboardButton(
            text=messages.BUTTON_ASK_QUESTION,
            callback_data="ask_custom_question"
        )
    )

    builder.adjust(1)  # По 1 кнопке в ряд

    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Назад"""
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text=messages.BUTTON_BACK,
            callback_data="back_to_menu"
        )
    )

    return builder.as_markup()


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура админ панели"""
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text=messages.BUTTON_ADMIN_CREATE_WEBINAR,
            callback_data="admin_create_webinar"
        )
    )

    builder.add(
        InlineKeyboardButton(
            text=messages.BUTTON_ADMIN_VIEW_STATS,
            callback_data="admin_view_stats"
        )
    )

    builder.adjust(1)  # По 1 кнопке в ряд

    return builder.as_markup()


def get_webinars_list_keyboard(webinars: list) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком вебинаров

    Args:
        webinars: Список вебинаров из БД

    Returns:
        InlineKeyboardMarkup с кнопками для каждого вебинара
    """
    builder = InlineKeyboardBuilder()

    for webinar in webinars:
        # Форматируем дату для отображения
        date_str = webinar.event_datetime.strftime("%d.%m %H:%M")

        # Обрезаем длинное название
        title = webinar.title if len(webinar.title) <= 40 else webinar.title[:37] + "..."

        # Создаем текст кнопки
        button_text = f"🎓 {title} ({date_str})"

        builder.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"select_webinar_{webinar.id}"
            )
        )

    builder.adjust(1)  # По 1 кнопке в ряд

    return builder.as_markup()
