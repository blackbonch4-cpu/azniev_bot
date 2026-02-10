"""
CRUD операции для работы с базой данных

Create, Read, Update, Delete операции для всех моделей
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import User, Webinar, Purchase, FAQQuestion, SupportTicket, AppSettings


# ===== USER CRUD =====

async def create_user(
    session: AsyncSession,
    telegram_id: int,
    email: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
) -> User:
    """Создать нового пользователя"""
    user = User(
        telegram_id=telegram_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        username=username,
        is_subscribed=True,  # При регистрации пользователь уже подписан
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Получить пользователя по Telegram ID"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Получить пользователя по email"""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def update_user_subscription(session: AsyncSession, telegram_id: int, is_subscribed: bool) -> None:
    """Обновить статус подписки пользователя"""
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(is_subscribed=is_subscribed)
    )
    await session.commit()


async def update_user_last_interaction(session: AsyncSession, telegram_id: int) -> None:
    """Обновить время последнего взаимодействия"""
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(last_interaction=datetime.now())
    )
    await session.commit()


# ===== WEBINAR CRUD =====

async def create_webinar(
    session: AsyncSession,
    title: str,
    date: datetime,
    price: float,
    description: Optional[str] = None,
    payment_link: Optional[str] = None,
    location: Optional[str] = None,
) -> Webinar:
    """Создать новый вебинар"""
    webinar = Webinar(
        title=title,
        description=description,
        date=date,
        price=price,
        payment_link=payment_link,
        location=location,
        is_active=True,
    )
    session.add(webinar)
    await session.commit()
    await session.refresh(webinar)
    return webinar


async def get_active_webinar(session: AsyncSession) -> Optional[Webinar]:
    """Получить активный вебинар (ближайший по дате)"""
    result = await session.execute(
        select(Webinar)
        .where(and_(Webinar.is_active == True, Webinar.event_datetime > datetime.now()))
        .order_by(Webinar.event_datetime)
    )
    return result.scalar_one_or_none()


async def get_webinar_by_id(session: AsyncSession, webinar_id: int) -> Optional[Webinar]:
    """Получить вебинар по ID"""
    result = await session.execute(
        select(Webinar).where(Webinar.id == webinar_id)
    )
    return result.scalar_one_or_none()


async def get_all_active_webinars(session: AsyncSession) -> List[Webinar]:
    """Получить все активные вебинары"""
    result = await session.execute(
        select(Webinar)
        .where(and_(Webinar.is_active == True, Webinar.event_datetime > datetime.now()))
        .order_by(Webinar.event_datetime)
    )
    return list(result.scalars().all())


async def deactivate_webinar(session: AsyncSession, webinar_id: int) -> None:
    """Деактивировать вебинар"""
    await session.execute(
        update(Webinar)
        .where(Webinar.id == webinar_id)
        .values(is_active=False)
    )
    await session.commit()


# ===== PURCHASE CRUD =====

async def create_purchase(
    session: AsyncSession,
    user_id: int,
    webinar_id: int,
    payment_id: Optional[str] = None,
    payment_status: str = "pending",
) -> Purchase:
    """Создать новую покупку"""
    purchase = Purchase(
        user_id=user_id,
        webinar_id=webinar_id,
        payment_id=payment_id,
        payment_status=payment_status,
    )
    session.add(purchase)
    await session.commit()
    await session.refresh(purchase)
    return purchase


async def get_user_purchase_for_webinar(
    session: AsyncSession,
    telegram_id: int,
    webinar_id: int
) -> Optional[Purchase]:
    """Проверить, купил ли пользователь билет на вебинар"""
    result = await session.execute(
        select(Purchase)
        .join(User)
        .where(
            and_(
                User.telegram_id == telegram_id,
                Purchase.webinar_id == webinar_id,
                Purchase.payment_status == "succeeded"
            )
        )
    )
    return result.scalar_one_or_none()


async def get_user_purchases(session: AsyncSession, telegram_id: int) -> List[Purchase]:
    """Получить все покупки пользователя"""
    result = await session.execute(
        select(Purchase)
        .join(User)
        .where(User.telegram_id == telegram_id)
        .options(selectinload(Purchase.webinar))
        .order_by(Purchase.purchase_date.desc())
    )
    return list(result.scalars().all())


async def get_purchase_by_payment_id(
    session: AsyncSession,
    payment_id: str
) -> Optional[Purchase]:
    """Получить покупку по ID платежа из ЮKassa"""
    result = await session.execute(
        select(Purchase)
        .where(Purchase.payment_id == payment_id)
        .options(selectinload(Purchase.user), selectinload(Purchase.webinar))
    )
    return result.scalar_one_or_none()


async def update_purchase_status(
    session: AsyncSession,
    payment_id: str,
    payment_status: str
) -> Optional[Purchase]:
    """Обновить статус платежа"""
    result = await session.execute(
        select(Purchase).where(Purchase.payment_id == payment_id)
    )
    purchase = result.scalar_one_or_none()

    if purchase:
        purchase.payment_status = payment_status
        await session.commit()
        await session.refresh(purchase)

    return purchase


async def get_purchases_for_reminder(
    session: AsyncSession,
    hours_before: int,
    notification_field: str
) -> List[Purchase]:
    """
    Получить покупки для отправки напоминаний

    Args:
        hours_before: За сколько часов до вебинара
        notification_field: Поле для проверки (notification_24h_sent или notification_1h_sent)
    """
    from datetime import timedelta

    now = datetime.now()
    target_time = now + timedelta(hours=hours_before)

    # Вебинары, которые начнутся примерно через hours_before часов (±15 минут)
    result = await session.execute(
        select(Purchase)
        .join(Webinar)
        .join(User)
        .where(
            and_(
                Purchase.payment_status == "succeeded",
                getattr(Purchase, notification_field) == False,
                Webinar.event_datetime >= target_time - timedelta(minutes=15),
                Webinar.event_datetime <= target_time + timedelta(minutes=15),
            )
        )
        .options(selectinload(Purchase.webinar), selectinload(Purchase.user))
    )
    return list(result.scalars().all())


async def mark_notification_sent(
    session: AsyncSession,
    purchase_id: int,
    notification_type: str
) -> None:
    """Пометить что напоминание отправлено"""
    field_map = {
        "24h": "notification_24h_sent",
        "1h": "notification_1h_sent",
    }

    field = field_map.get(notification_type)
    if field:
        await session.execute(
            update(Purchase)
            .where(Purchase.id == purchase_id)
            .values(**{field: True})
        )
        await session.commit()


# ===== FAQ CRUD =====

async def create_faq_question(session: AsyncSession, question: str, answer: str, order_index: int = 0) -> FAQQuestion:
    """Создать FAQ вопрос"""
    faq = FAQQuestion(
        question=question,
        answer=answer,
        order_index=order_index,
    )
    session.add(faq)
    await session.commit()
    await session.refresh(faq)
    return faq


async def get_all_faq(session: AsyncSession) -> List[FAQQuestion]:
    """Получить все FAQ вопросы"""
    result = await session.execute(
        select(FAQQuestion).order_by(FAQQuestion.order_index)
    )
    return list(result.scalars().all())


# ===== SUPPORT TICKET CRUD =====

async def create_support_ticket(session: AsyncSession, user_id: int, question: str) -> SupportTicket:
    """Создать обращение в поддержку"""
    ticket = SupportTicket(
        user_id=user_id,
        question=question,
    )
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket


async def get_open_tickets(session: AsyncSession) -> List[SupportTicket]:
    """Получить все открытые обращения"""
    result = await session.execute(
        select(SupportTicket)
        .where(SupportTicket.status == "open")
        .options(selectinload(SupportTicket.user))
        .order_by(SupportTicket.created_at.desc())
    )
    return list(result.scalars().all())


async def close_support_ticket(session: AsyncSession, ticket_id: int) -> None:
    """Закрыть обращение в поддержку"""
    await session.execute(
        update(SupportTicket)
        .where(SupportTicket.id == ticket_id)
        .values(status="closed")
    )
    await session.commit()


# ===== СТАТИСТИКА =====

async def get_users_count(session: AsyncSession) -> int:
    """Получить общее количество пользователей"""
    from sqlalchemy import func
    result = await session.execute(
        select(func.count(User.id))
    )
    return result.scalar() or 0


async def get_webinars_count(session: AsyncSession) -> int:
    """Получить общее количество вебинаров"""
    from sqlalchemy import func
    result = await session.execute(
        select(func.count(Webinar.id))
    )
    return result.scalar() or 0


async def get_purchases_count(session: AsyncSession) -> int:
    """Получить общее количество покупок"""
    from sqlalchemy import func
    result = await session.execute(
        select(func.count(Purchase.id)).where(Purchase.payment_status == "succeeded")
    )
    return result.scalar() or 0


async def get_webinar_purchases_count(session: AsyncSession, webinar_id: int) -> int:
    """Получить количество покупок для конкретного вебинара"""
    from sqlalchemy import func
    result = await session.execute(
        select(func.count(Purchase.id))
        .where(Purchase.webinar_id == webinar_id)
        .where(Purchase.payment_status == "succeeded")
    )
    return result.scalar() or 0


# ===== WEBINAR IMAGE CRUD =====

async def update_webinar_image(
    session: AsyncSession,
    webinar_id: int,
    image_file_id: str,
    image_url: str,
    thumbnail_file_id: Optional[str] = None
) -> Optional[Webinar]:
    """Обновить изображение вебинара"""
    await session.execute(
        update(Webinar)
        .where(Webinar.id == webinar_id)
        .values(
            image_file_id=image_file_id,
            image_url=image_url,
            thumbnail_file_id=thumbnail_file_id or image_file_id
        )
    )
    await session.commit()

    # Вернуть обновленный вебинар
    result = await session.execute(
        select(Webinar).where(Webinar.id == webinar_id)
    )
    return result.scalar_one_or_none()


async def get_all_webinars_with_images(session: AsyncSession) -> List[Webinar]:
    """Получить все активные вебинары с изображениями для галереи"""
    result = await session.execute(
        select(Webinar)
        .where(Webinar.is_active == True)
        .order_by(Webinar.event_datetime)
    )
    return list(result.scalars().all())


# ===== APP SETTINGS CRUD =====

async def get_setting(session: AsyncSession, key: str) -> Optional[str]:
    """Получить настройку по ключу"""
    result = await session.execute(
        select(AppSettings).where(AppSettings.key == key)
    )
    setting = result.scalar_one_or_none()
    return setting.value if setting else None


async def set_setting(session: AsyncSession, key: str, value: str) -> AppSettings:
    """Установить или обновить настройку"""
    # Проверить, существует ли настройка
    result = await session.execute(
        select(AppSettings).where(AppSettings.key == key)
    )
    setting = result.scalar_one_or_none()

    if setting:
        # Обновить существующую
        await session.execute(
            update(AppSettings)
            .where(AppSettings.key == key)
            .values(value=value, updated_at=datetime.now())
        )
    else:
        # Создать новую
        setting = AppSettings(key=key, value=value)
        session.add(setting)

    await session.commit()

    # Вернуть обновленную настройку
    result = await session.execute(
        select(AppSettings).where(AppSettings.key == key)
    )
    return result.scalar_one()


async def get_all_settings(session: AsyncSession) -> dict:
    """Получить все настройки в виде словаря"""
    result = await session.execute(
        select(AppSettings)
    )
    settings = result.scalars().all()
    return {setting.key: setting.value for setting in settings}
