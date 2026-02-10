"""
Сервис для интеграции с ЮKassa

Документация: https://yookassa.ru/developers/api
"""

import logging
from typing import Optional
from decimal import Decimal
from yookassa import Configuration, Payment

from bot.config import settings

logger = logging.getLogger(__name__)

# Конфигурация ЮKassa
Configuration.account_id = settings.yookassa_shop_id
Configuration.secret_key = settings.yookassa_secret_key


def create_payment(
    amount: Decimal,
    description: str,
    return_url: str = None,
    metadata: dict = None
) -> Optional[dict]:
    """
    Создать платеж через ЮKassa

    Args:
        amount: Сумма платежа в рублях (например, 2500.00)
        description: Описание платежа
        return_url: URL для возврата после оплаты (опционально)
        metadata: Дополнительные данные (например, user_id, webinar_id)

    Returns:
        dict с данными платежа или None в случае ошибки

    Пример возвращаемых данных:
    {
        'id': '2d8a7e8b-000f-5000-8000-18db351245c7',
        'status': 'pending',
        'amount': {'value': '2500.00', 'currency': 'RUB'},
        'confirmation': {
            'type': 'redirect',
            'confirmation_url': 'https://yoomoney.ru/checkout/payments/v2/contract?orderId=...'
        },
        'created_at': '2026-02-09T12:00:00.000Z',
        'metadata': {...}
    }
    """
    try:
        logger.info(f"Создание платежа: сумма={amount}, описание={description}")

        # Подготовка данных платежа
        payment_data = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url or "https://t.me/your_bot"  # TODO: указать реальный URL
            },
            "capture": True,  # Автоматическое списание
            "description": description
        }

        # Добавляем метаданные если есть
        if metadata:
            payment_data["metadata"] = metadata

        # Создаем платеж
        payment = Payment.create(payment_data)

        logger.info(f"Платеж создан успешно: ID={payment.id}, status={payment.status}")

        # Возвращаем данные платежа
        return {
            'id': payment.id,
            'status': payment.status,
            'amount': payment.amount.value,
            'currency': payment.amount.currency,
            'confirmation_url': payment.confirmation.confirmation_url,
            'created_at': payment.created_at,
            'metadata': payment.metadata
        }

    except Exception as e:
        logger.error(f"Ошибка при создании платежа: {e}", exc_info=True)
        return None


def get_payment_status(payment_id: str) -> Optional[dict]:
    """
    Получить статус платежа по ID

    Args:
        payment_id: ID платежа в ЮKassa

    Returns:
        dict с данными платежа или None в случае ошибки

    Возможные статусы:
    - pending: ожидает оплаты
    - waiting_for_capture: ожидает подтверждения
    - succeeded: успешно оплачен
    - canceled: отменен
    """
    try:
        logger.info(f"Проверка статуса платежа: {payment_id}")

        payment = Payment.find_one(payment_id)

        logger.info(f"Статус платежа {payment_id}: {payment.status}")

        return {
            'id': payment.id,
            'status': payment.status,
            'amount': payment.amount.value,
            'currency': payment.amount.currency,
            'paid': payment.paid,
            'created_at': payment.created_at,
            'metadata': payment.metadata
        }

    except Exception as e:
        logger.error(f"Ошибка при получении статуса платежа {payment_id}: {e}", exc_info=True)
        return None


def cancel_payment(payment_id: str) -> bool:
    """
    Отменить платеж

    Args:
        payment_id: ID платежа в ЮKassa

    Returns:
        True если отменен успешно, False в случае ошибки
    """
    try:
        logger.info(f"Отмена платежа: {payment_id}")

        payment = Payment.cancel(payment_id)

        logger.info(f"Платеж {payment_id} отменен, статус: {payment.status}")

        return payment.status == "canceled"

    except Exception as e:
        logger.error(f"Ошибка при отмене платежа {payment_id}: {e}", exc_info=True)
        return False


def format_payment_link_message(
    webinar_title: str,
    price: Decimal,
    confirmation_url: str
) -> str:
    """
    Форматировать сообщение со ссылкой на оплату

    Args:
        webinar_title: Название вебинара
        price: Стоимость
        confirmation_url: Ссылка на оплату от ЮKassa

    Returns:
        Отформатированное сообщение
    """
    from bot.texts import messages

    return messages.PAYMENT_LINK_MESSAGE.format(
        title=webinar_title,
        price=f"{price:.0f}",
        payment_link=confirmation_url
    )
