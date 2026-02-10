"""
Валидаторы для проверки данных
"""

import re
from datetime import datetime
from typing import Tuple, Optional


def validate_email(email: str) -> bool:
    """
    Валидация email адреса

    Args:
        email: Email адрес для проверки

    Returns:
        True если email корректен, иначе False
    """
    # Регулярное выражение для проверки email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))


def validate_date(date_str: str) -> Tuple[bool, Optional[datetime]]:
    """
    Валидация даты в формате ДД.ММ.ГГГГ ЧЧ:ММ

    Args:
        date_str: Строка с датой

    Returns:
        Tuple (is_valid, datetime_object)
    """
    try:
        # Пробуем распарсить дату
        dt = datetime.strptime(date_str.strip(), "%d.%m.%Y %H:%M")

        # Проверяем что дата в будущем
        if dt <= datetime.now():
            return False, None

        return True, dt
    except ValueError:
        return False, None


def validate_price(price_str: str) -> Tuple[bool, Optional[float]]:
    """
    Валидация цены

    Args:
        price_str: Строка с ценой

    Returns:
        Tuple (is_valid, price_float)
    """
    try:
        price = float(price_str.strip())

        # Цена должна быть положительной
        if price <= 0:
            return False, None

        return True, price
    except ValueError:
        return False, None


def validate_url(url: str) -> bool:
    """
    Валидация URL

    Args:
        url: URL для проверки

    Returns:
        True если URL корректен, иначе False
    """
    url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
    return bool(re.match(url_pattern, url.strip()))
