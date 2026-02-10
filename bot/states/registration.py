"""
FSM States для процесса регистрации пользователя

Используется для управления диалогом при регистрации
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Состояния для регистрации пользователя"""

    # Ожидание email от пользователя
    waiting_for_email = State()
