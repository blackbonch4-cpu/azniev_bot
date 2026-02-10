"""
API handlers для обработки HTTP запросов

Все обработчики возвращают JSON ответы
"""

import logging
from datetime import datetime
from typing import Optional
from aiohttp import web
from aiogram import Bot

from bot.database.db_setup import async_session_maker
from bot.database import crud
from bot.config import settings

logger = logging.getLogger(__name__)


async def get_webinars(request: web.Request) -> web.Response:
    """
    GET /api/v1/webinars?telegram_id={id}

    Получить список всех активных вебинаров с флагом is_purchased
    """
    try:
        telegram_id = request.query.get('telegram_id')
        if not telegram_id:
            return web.json_response(
                {'error': 'telegram_id is required'},
                status=400
            )

        telegram_id = int(telegram_id)

        async with async_session_maker() as session:
            # Получить все активные вебинары
            webinars = await crud.get_all_webinars_with_images(session)

            # Получить пользователя для проверки покупок
            user = await crud.get_user_by_telegram_id(session, telegram_id)

            # Сформировать ответ
            webinars_data = []
            for webinar in webinars:
                # Проверить, купил ли пользователь этот вебинар
                is_purchased = False
                group_link = None

                if user:
                    purchase = await crud.get_user_purchase_for_webinar(
                        session, user.id, webinar.id
                    )
                    if purchase and purchase.payment_status == 'succeeded':
                        is_purchased = True
                        group_link = webinar.group_link

                webinars_data.append({
                    'id': webinar.id,
                    'title': webinar.title,
                    'description': webinar.description,
                    'event_datetime': webinar.event_datetime.isoformat(),
                    'price': float(webinar.price),
                    'location': webinar.location,
                    'image_url': webinar.image_url,
                    'thumbnail_url': webinar.image_url,  # Можно использовать thumbnail_file_id если нужен меньший размер
                    'is_purchased': is_purchased,
                    'payment_link': webinar.payment_link if not is_purchased else None,
                    'group_link': group_link
                })

            return web.json_response({'webinars': webinars_data})

    except ValueError:
        return web.json_response(
            {'error': 'Invalid telegram_id format'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error in get_webinars: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )


async def get_purchases(request: web.Request) -> web.Response:
    """
    GET /api/v1/purchases?telegram_id={id}

    Получить историю покупок пользователя
    """
    try:
        telegram_id = request.query.get('telegram_id')
        if not telegram_id:
            return web.json_response(
                {'error': 'telegram_id is required'},
                status=400
            )

        telegram_id = int(telegram_id)

        async with async_session_maker() as session:
            # Получить пользователя
            user = await crud.get_user_by_telegram_id(session, telegram_id)
            if not user:
                return web.json_response({'purchases': []})

            # Получить все покупки
            purchases = await crud.get_user_purchases(session, user.id)

            # Фильтровать только успешные
            purchases = [p for p in purchases if p.payment_status == 'succeeded']

            # Сформировать ответ
            purchases_data = []
            for purchase in purchases:
                is_upcoming = purchase.webinar.event_datetime > datetime.now()

                purchases_data.append({
                    'id': purchase.id,
                    'webinar': {
                        'id': purchase.webinar.id,
                        'title': purchase.webinar.title,
                        'event_datetime': purchase.webinar.event_datetime.isoformat(),
                        'price': float(purchase.webinar.price),
                        'image_url': purchase.webinar.image_url,
                        'group_link': purchase.webinar.group_link
                    },
                    'purchase_date': purchase.purchase_date.isoformat(),
                    'payment_status': purchase.payment_status,
                    'is_upcoming': is_upcoming
                })

            # Сортировать: сначала предстоящие, потом прошедшие
            purchases_data.sort(
                key=lambda x: (not x['is_upcoming'], x['webinar']['event_datetime']),
                reverse=True
            )

            return web.json_response({'purchases': purchases_data})

    except ValueError:
        return web.json_response(
            {'error': 'Invalid telegram_id format'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error in get_purchases: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )


async def get_profile(request: web.Request) -> web.Response:
    """
    GET /api/v1/profile?telegram_id={id}

    Получить профиль пользователя
    """
    try:
        telegram_id = request.query.get('telegram_id')
        if not telegram_id:
            return web.json_response(
                {'error': 'telegram_id is required'},
                status=400
            )

        telegram_id = int(telegram_id)

        async with async_session_maker() as session:
            # Получить пользователя
            user = await crud.get_user_by_telegram_id(session, telegram_id)
            if not user:
                return web.json_response(
                    {'error': 'User not found'},
                    status=404
                )

            # Получить количество покупок
            purchases = await crud.get_user_purchases(session, user.id)
            total_purchases = len([p for p in purchases if p.payment_status == 'succeeded'])

            # Сформировать ответ
            user_data = {
                'telegram_id': user.telegram_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'avatar_url': None,  # Можно добавить поле в модель User, если нужно
                'registration_date': user.registration_date.isoformat(),
                'total_purchases': total_purchases
            }

            return web.json_response({'user': user_data})

    except ValueError:
        return web.json_response(
            {'error': 'Invalid telegram_id format'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error in get_profile: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )


async def get_settings(request: web.Request) -> web.Response:
    """
    GET /api/v1/settings

    Получить настройки приложения (соцсети)
    """
    try:
        async with async_session_maker() as session:
            settings_dict = await crud.get_all_settings(session)

            social_links = {
                'instagram': settings_dict.get('social_instagram'),
                'telegram': settings_dict.get('social_telegram'),
                'website': settings_dict.get('social_website')
            }

            return web.json_response({'social_links': social_links})

    except Exception as e:
        logger.error(f"Error in get_settings: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )


async def create_support_ticket(request: web.Request) -> web.Response:
    """
    POST /api/v1/support/ticket

    Создать тикет в поддержку и отправить сообщение в супергруппу
    """
    try:
        data = await request.json()

        telegram_id = data.get('telegram_id')
        question = data.get('question')

        if not telegram_id or not question:
            return web.json_response(
                {'error': 'telegram_id and question are required'},
                status=400
            )

        if len(question) < 10:
            return web.json_response(
                {'error': 'Question is too short (minimum 10 characters)'},
                status=400
            )

        telegram_id = int(telegram_id)

        async with async_session_maker() as session:
            # Получить пользователя
            user = await crud.get_user_by_telegram_id(session, telegram_id)
            if not user:
                return web.json_response(
                    {'error': 'User not found'},
                    status=404
                )

            # Создать тикет
            ticket = await crud.create_support_ticket(
                session=session,
                user_id=user.id,
                question=question
            )

            # Отправить сообщение в супергруппу
            bot: Bot = request.app['bot']
            user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username_mention = f"@{user.username}" if user.username else "без username"

            support_message = (
                f"❓ **Новый вопрос в поддержку**\n\n"
                f"👤 **От:** {user_name} ({username_mention})\n"
                f"📧 **Email:** {user.email}\n"
                f"🆔 **Telegram ID:** {user.telegram_id}\n\n"
                f"**Вопрос:**\n{question}"
            )

            await bot.send_message(
                chat_id=settings.support_group_id,
                text=support_message,
                message_thread_id=settings.support_topic_id if settings.support_topic_id else None
            )

            return web.json_response({
                'success': True,
                'ticket_id': ticket.id,
                'message': 'Ваш вопрос отправлен в поддержку'
            })

    except ValueError:
        return web.json_response(
            {'error': 'Invalid data format'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error in create_support_ticket: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )
