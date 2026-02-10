"""
Конфигурация бота

Все настройки загружаются из переменных окружения (.env файл)
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""

    # Telegram Bot
    bot_token: str = Field(..., description="Telegram Bot API Token")

    # Telegram Channel/Group
    channel_id: int = Field(..., description="ID приватного канала для проверки подписки")

    # Admins
    admin_ids: str = Field(..., description="Telegram IDs администраторов через запятую")

    # Support
    support_group_id: int = Field(..., description="ID супергруппы для поддержки")
    support_topic_id: int = Field(default=1, description="ID темы в супергруппе")

    # YooKassa
    yookassa_shop_id: str = Field(..., description="YooKassa Shop ID")
    yookassa_secret_key: str = Field(..., description="YooKassa Secret Key")

    # Google Sheets
    google_sheets_creds_file: str = Field(default="credentials.json", description="Путь к credentials файлу")
    google_sheet_id: str = Field(..., description="ID Google Таблицы")

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./database.db", description="Database URL")

    # Scheduler
    sheets_sync_interval: int = Field(default=30, description="Интервал синхронизации с Google Sheets (минуты)")
    reminder_check_interval: int = Field(default=10, description="Интервал проверки напоминаний (минуты)")

    # Logging
    log_level: str = Field(default="INFO", description="Уровень логирования")

    # API Server
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8080, description="API server port")
    api_cors_origins: str = Field(default="*", description="CORS origins")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def admin_ids_list(self) -> List[int]:
        """Список ID администраторов"""
        return [int(admin_id.strip()) for admin_id in self.admin_ids.split(",")]

    def is_admin(self, user_id: int) -> bool:
        """Проверка является ли пользователь администратором"""
        return user_id in self.admin_ids_list


# Глобальный экземпляр настроек
settings = Settings()
