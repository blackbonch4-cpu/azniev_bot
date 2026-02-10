"""
FSM состояния для системы поддержки

Используются для диалогов с пользователем при задавании вопросов в поддержку.
"""

from aiogram.fsm.state import State, StatesGroup


class SupportStates(StatesGroup):
    """Состояния для работы с поддержкой"""

    waiting_for_question = State()  # Ожидание вопроса от пользователя
