"""
FSM состояния для админ панели

Используются для диалогов с администратором при создании вебинаров.
"""

from aiogram.fsm.state import State, StatesGroup


class AdminWebinarStates(StatesGroup):
    """Состояния для создания вебинара"""

    waiting_for_title = State()         # Ожидание названия
    waiting_for_description = State()   # Ожидание описания
    waiting_for_date = State()          # Ожидание даты и времени
    waiting_for_price = State()         # Ожидание стоимости
    waiting_for_location = State()      # Ожидание места/ссылки
    waiting_for_payment_link = State()  # Ожидание ссылки на оплату (опционально)
