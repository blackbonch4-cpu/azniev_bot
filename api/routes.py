"""
API маршруты

Определяет все endpoints и связывает их с handlers
"""

from aiohttp import web
from api import handlers, admin_handlers


def setup_routes(app: web.Application):
    """Настроить маршруты API"""
    # Public endpoints
    app.router.add_get('/api/v1/webinars', handlers.get_webinars)
    app.router.add_get('/api/v1/purchases', handlers.get_purchases)
    app.router.add_get('/api/v1/profile', handlers.get_profile)
    app.router.add_get('/api/v1/settings', handlers.get_settings)
    app.router.add_post('/api/v1/support/ticket', handlers.create_support_ticket)

    # Admin endpoints
    app.router.add_post('/api/v1/admin/webinars', admin_handlers.create_webinar)
    app.router.add_put('/api/v1/admin/webinars/{id}', admin_handlers.update_webinar)
    app.router.add_delete('/api/v1/admin/webinars/{id}', admin_handlers.delete_webinar)
    app.router.add_post('/api/v1/admin/upload', admin_handlers.upload_image)
    app.router.add_post('/api/v1/admin/social-links', admin_handlers.update_social_links)

    # Health check endpoint
    app.router.add_get('/api/v1/health', lambda request: web.json_response({'status': 'ok'}))
