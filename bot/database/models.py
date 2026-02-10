"""
SQLAlchemy модели для базы данных

Все модели описывают структуру таблиц в SQLite
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, String, Boolean, DateTime, Integer, Numeric, Text, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    last_interaction: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    purchases: Mapped[List["Purchase"]] = relationship("Purchase", back_populates="user", cascade="all, delete-orphan")
    support_tickets: Mapped[List["SupportTicket"]] = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, email={self.email})>"


class Webinar(Base):
    """Модель вебинара"""
    __tablename__ = "webinars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_link: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # Ручная ссылка или NULL
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Онлайн ссылка или адрес
    group_link: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # Ссылка на группу вебинара
    image_file_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Telegram file_id фото курса
    image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # URL для получения фото
    thumbnail_file_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Миниатюра для галереи
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    purchases: Mapped[List["Purchase"]] = relationship("Purchase", back_populates="webinar", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Webinar(id={self.id}, title={self.title}, date={self.event_datetime})>"


class Purchase(Base):
    """Модель покупки/участия в вебинаре"""
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    webinar_id: Mapped[int] = mapped_column(Integer, ForeignKey("webinars.id"), nullable=False, index=True)
    payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # ID платежа в ЮKassa
    payment_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)  # pending, succeeded, canceled
    purchase_date: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    notification_24h_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notification_1h_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="purchases")
    webinar: Mapped["Webinar"] = relationship("Webinar", back_populates="purchases")

    def __repr__(self) -> str:
        return f"<Purchase(id={self.id}, user_id={self.user_id}, webinar_id={self.webinar_id}, status={self.payment_status})>"


class FAQQuestion(Base):
    """Модель FAQ вопроса"""
    __tablename__ = "faq_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<FAQQuestion(id={self.id}, question={self.question[:50]})>"


class SupportTicket(Base):
    """Модель вопроса в поддержку"""
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False, index=True)  # open, closed

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="support_tickets")

    def __repr__(self) -> str:
        return f"<SupportTicket(id={self.id}, user_id={self.user_id}, status={self.status})>"


class AppSettings(Base):
    """Модель настроек приложения"""
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<AppSettings(key={self.key}, value={self.value[:50] if self.value else None})>"
