"""
Admin API handlers для управления вебинарами через MiniApp

Доступны только для пользователей из ADMIN_IDS
"""

import logging
import base64
from datetime import datetime
from typing import Optional
from decimal import Decimal
from aiohttp import web
from aiogram import Bot

from bot.database.db_setup import async_session_maker
from bot.database import crud
from bot.database.models import Webinar
from bot.config import settings

logger = logging.getLogger(__name__)


def check_admin(telegram_id: int) -> bool:
    """Проверить, является ли пользователь админом"""
    return settings.is_admin(telegram_id)


async def create_webinar(request: web.Request) -> web.Response:
    """
    POST /api/v1/admin/webinars

    Создать новый вебинар

    Body:
    {
        "telegram_id": 123,
        "title": "Название",
        "description": "Описание",
        "event_datetime": "2026-03-15T18:00:00",
        "price": 5000,
        "location": "Online",
        "group_link": "https://t.me/...",
        "payment_link": "https://...",
        "image_url": "https://..." (опционально)
    }
    """
    try:
        data = await request.json()

        telegram_id = data.get('telegram_id')
        if not telegram_id or not check_admin(int(telegram_id)):
            return web.json_response(
                {'error': 'Access denied'},
                status=403
            )

        # Валидация обязательных полей
        required_fields = ['title', 'event_datetime', 'price']
        for field in required_fields:
            if field not in data:
                return web.json_response(
                    {'error': f'Missing required field: {field}'},
                    status=400
                )

        # Парсинг даты
        try:
            event_datetime = datetime.fromisoformat(data['event_datetime'].replace('Z', '+00:00'))
        except ValueError:
            return web.json_response(
                {'error': 'Invalid datetime format. Use ISO format: 2026-03-15T18:00:00'},
                status=400
            )

        # Создание вебинара
        async with async_session_maker() as session:
            webinar = await crud.create_webinar(
                session=session,
                title=data['title'],
                description=data.get('description'),
                date=event_datetime,
                price=float(data['price']),
                location=data.get('location'),
                payment_link=data.get('payment_link'),
                group_link=data.get('group_link')
            )

            # Если есть изображение, обновить
            if data.get('image_url'):
                await crud.update_webinar_image(
                    session=session,
                    webinar_id=webinar.id,
                    image_file_id='',  # Пустая строка, т.к. загружаем через URL
                    image_url=data['image_url'],
                    thumbnail_file_id=''
                )

            return web.json_response({
                'success': True,
                'webinar': {
                    'id': webinar.id,
                    'title': webinar.title,
                    'description': webinar.description,
                    'event_datetime': webinar.event_datetime.isoformat(),
                    'price': float(webinar.price),
                    'location': webinar.location,
                    'group_link': webinar.group_link,
                    'payment_link': webinar.payment_link,
                    'image_url': data.get('image_url'),
                    'is_active': webinar.is_active
                }
            })

    except Exception as e:
        logger.error(f"Error in create_webinar: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )


async def update_webinar(request: web.Request) -> web.Response:
    """
    PUT /api/v1/admin/webinars/{id}

    Обновить вебинар
    """
    try:
        webinar_id = int(request.match_info['id'])
        data = await request.json()

        telegram_id = data.get('telegram_id')
        if not telegram_id or not check_admin(int(telegram_id)):
            return web.json_response(
                {'error': 'Access denied'},
                status=403
            )

        async with async_session_maker() as session:
            # Проверить существование вебинара
            webinar = await crud.get_webinar_by_id(session, webinar_id)
            if not webinar:
                return web.json_response(
                    {'error': 'Webinar not found'},
                    status=404
                )

            # Обновить поля
            update_data = {}

            if 'title' in data:
                update_data['title'] = data['title']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'event_datetime' in data:
                update_data['event_datetime'] = datetime.fromisoformat(
                    data['event_datetime'].replace('Z', '+00:00')
                )
            if 'price' in data:
                update_data['price'] = Decimal(str(data['price']))
            if 'location' in data:
                update_data['location'] = data['location']
            if 'group_link' in data:
                update_data['group_link'] = data['group_link']
            if 'payment_link' in data:
                update_data['payment_link'] = data['payment_link']
            if 'is_active' in data:
                update_data['is_active'] = data['is_active']

            # Обновить в БД
            from sqlalchemy import update as sql_update
            stmt = sql_update(Webinar).where(
                Webinar.id == webinar_id
            ).values(**update_data)
            await session.execute(stmt)
            await session.commit()

            # Если есть новое изображение
            if data.get('image_url'):
                await crud.update_webinar_image(
                    session=session,
                    webinar_id=webinar_id,
                    image_file_id='',
                    image_url=data['image_url'],
                    thumbnail_file_id=''
                )

            # Получить обновленный вебинар
            webinar = await crud.get_webinar_by_id(session, webinar_id)

            return web.json_response({
                'success': True,
                'webinar': {
                    'id': webinar.id,
                    'title': webinar.title,
                    'description': webinar.description,
                    'event_datetime': webinar.event_datetime.isoformat(),
                    'price': float(webinar.price),
                    'location': webinar.location,
                    'group_link': webinar.group_link,
                    'payment_link': webinar.payment_link,
                    'image_url': webinar.image_url,
                    'is_active': webinar.is_active
                }
            })

    except ValueError as e:
        return web.json_response(
            {'error': f'Invalid data: {str(e)}'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error in update_webinar: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )


async def delete_webinar(request: web.Request) -> web.Response:
    """
    DELETE /api/v1/admin/webinars/{id}

    Удалить (деактивировать) вебинар
    """
    try:
        webinar_id = int(request.match_info['id'])
        telegram_id = int(request.query.get('telegram_id', 0))

        if not check_admin(telegram_id):
            return web.json_response(
                {'error': 'Access denied'},
                status=403
            )

        async with async_session_maker() as session:
            # Деактивировать вебинар
            webinar = await crud.deactivate_webinar(session, webinar_id)
            if not webinar:
                return web.json_response(
                    {'error': 'Webinar not found'},
                    status=404
                )

            return web.json_response({
                'success': True,
                'message': 'Webinar deactivated successfully'
            })

    except Exception as e:
        logger.error(f"Error in delete_webinar: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )


async def upload_image(request: web.Request) -> web.Response:
    """
    POST /api/v1/admin/upload

    Загрузить изображение (base64)

    Body:
    {
        "telegram_id": 123,
        "image": "data:image/jpeg;base64,/9j/4AAQ..."
    }

    Returns:
    {
        "success": true,
        "image_url": "https://api.telegram.org/file/..."
    }
    """
    try:
        data = await request.json()

        telegram_id = data.get('telegram_id')
        if not telegram_id or not check_admin(int(telegram_id)):
            return web.json_response(
                {'error': 'Access denied'},
                status=403
            )

        image_data = data.get('image')
        if not image_data:
            return web.json_response(
                {'error': 'Missing image data'},
                status=400
            )

        # Удалить префикс data:image/...;base64,
        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]

        # Декодировать base64
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception:
            return web.json_response(
                {'error': 'Invalid base64 image data'},
                status=400
            )

        # Отправить фото через бота и получить file_id
        bot: Bot = request.app['bot']

        # Отправить фото в личку боту (самому себе) чтобы получить file_id
        from io import BytesIO
        from aiogram.types import BufferedInputFile

        photo_file = BufferedInputFile(image_bytes, filename="upload.jpg")
        message = await bot.send_photo(
            chat_id=settings.admin_ids_list[0],  # Отправить первому админу
            photo=photo_file
        )

        # Получить file_id и URL
        photo = message.photo[-1]  # Самый большой размер
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{settings.bot_token}/{file.file_path}"

        return web.json_response({
            'success': True,
            'image_url': file_url,
            'file_id': photo.file_id
        })

    except Exception as e:
        logger.error(f"Error in upload_image: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )


async def update_social_links(request: web.Request) -> web.Response:
    """
    POST /api/v1/admin/social-links

    Обновить ссылки на соцсети

    Body:
    {
        "telegram_id": 123,
        "instagram": "https://instagram.com/...",
        "telegram": "https://t.me/...",
        "website": "https://example.com"
    }
    """
    try:
        data = await request.json()

        telegram_id = data.get('telegram_id')
        if not telegram_id or not check_admin(int(telegram_id)):
            return web.json_response(
                {'error': 'Access denied'},
                status=403
            )

        async with async_session_maker() as session:
            # Обновить соцсети
            if 'instagram' in data:
                await crud.set_setting(session, 'social_instagram', data['instagram'])
            if 'telegram' in data:
                await crud.set_setting(session, 'social_telegram', data['telegram'])
            if 'website' in data:
                await crud.set_setting(session, 'social_website', data['website'])

            return web.json_response({
                'success': True,
                'message': 'Social links updated successfully'
            })

    except Exception as e:
        logger.error(f"Error in update_social_links: {e}", exc_info=True)
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )
