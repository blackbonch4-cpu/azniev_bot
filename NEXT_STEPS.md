# 🎯 Следующие шаги разработки

## ✅ Что уже сделано

### 1. Базовая инфраструктура
- [x] Структура проекта
- [x] requirements.txt с зависимостями
- [x] .env.example с примерами переменных
- [x] .gitignore для безопасности
- [x] README.md с подробными инструкциями
- [x] run.py для быстрого запуска

### 2. Конфигурация
- [x] bot/config.py - централизованная конфигурация с pydantic
- [x] Загрузка переменных из .env
- [x] Проверка прав администратора

### 3. База данных
- [x] bot/database/models.py - все SQLAlchemy модели
  - User (пользователи)
  - Webinar (вебинары)
  - Purchase (покупки)
  - FAQQuestion (FAQ)
  - SupportTicket (обращения в поддержку)
- [x] bot/database/db_setup.py - инициализация БД
- [x] bot/database/crud.py - все CRUD операции

### 4. Утилиты
- [x] bot/utils/validators.py - валидация email, дат, цен, URL

### 5. Тексты
- [x] bot/texts/messages.py - все сообщения бота (легко редактировать!)
- [x] bot/texts/faq.py - FAQ вопросы и ответы

### 6. Точка входа
- [x] bot/main.py - главный файл с инициализацией

---

## 🚧 Что нужно реализовать

### Этап 1: Базовые handlers (регистрация и старт)

#### 1.1 Handler /start
Создать файл: `bot/handlers/start.py`

**Функционал:**
- Обработка команды /start
- Проверка подписки на канал
- Регистрация новых пользователей
- Запрос email с валидацией
- Главное меню для зарегистрированных

**FSM States:**
Создать файл: `bot/states/registration.py`
```python
from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_email = State()
```

**Что нужно:**
- Использовать `bot/texts/messages.py` для всех текстов
- Использовать `bot/utils/validators.py` для валидации email
- Использовать `bot/database/crud.py` для сохранения пользователя

#### 1.2 Middleware проверки подписки
Создать файл: `bot/middlewares/subscription_check.py`

**Функционал:**
- Проверка подписки на приватный канал перед каждой командой
- Если не подписан - предложить подписаться
- Кнопка "Проверить подписку"

**Что нужно:**
- Метод `bot.get_chat_member(channel_id, user_id)`
- Проверка статуса: member, administrator, creator

---

### Этап 2: Функционал вебинаров

#### 2.1 Handler "Вебинар"
Создать файл: `bot/handlers/webinar.py`

**Функционал:**
- Обработка команды/сообщения "Вебинар"
- Показ информации о ближайшем вебинаре
- Проверка - купил ли пользователь уже билет
- Если нет - показать ссылку на оплату
- Если да - показать информацию и напоминание

**Что нужно:**
- `crud.get_active_webinar()` - получить ближайший вебинар
- `crud.get_user_purchase_for_webinar()` - проверить покупку
- Кнопка "Оплатить" с payment_link

#### 2.2 Интеграция с ЮKassa
Создать файл: `bot/services/payment_service.py`

**Функционал:**
- Создание платежа через ЮKassa API
- Обработка webhook от ЮKassa
- Обновление статуса платежа в БД

**Документация:**
https://yookassa.ru/developers/api

**Основные методы:**
```python
from yookassa import Configuration, Payment

Configuration.account_id = settings.yookassa_shop_id
Configuration.secret_key = settings.yookassa_secret_key

# Создание платежа
payment = Payment.create({
    "amount": {
        "value": "2500.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://your-site.com/success"
    },
    "capture": True,
    "description": "Оплата вебинара"
})
```

#### 2.3 Handler обработки платежей
Создать файл: `bot/handlers/payments.py`

**Функционал:**
- Обработка callback от ЮKassa (webhook)
- Обновление статуса в БД
- Отправка поздравления пользователю
- Синхронизация с Google Sheets

---

### Этап 3: FAQ и поддержка

#### 3.1 Handler /help
Создать файл: `bot/handlers/support.py`

**Функционал:**
- Показ FAQ меню с inline кнопками
- Обработка нажатий на вопросы
- Кнопка "Задать свой вопрос"
- FSM для получения вопроса от пользователя
- Отправка вопроса в супергруппу в тему

**FSM States:**
Создать файл: `bot/states/support.py`
```python
class SupportStates(StatesGroup):
    waiting_for_question = State()
```

**Что нужно:**
- `bot.send_message(support_group_id, message, message_thread_id=topic_id)`
- Формат сообщения с информацией о пользователе

---

### Этап 4: Админ панель

#### 4.1 Middleware проверки админа
Создать файл: `bot/middlewares/admin_check.py`

**Функционал:**
- Проверка что пользователь в списке админов
- Фильтр для админских хэндлеров

#### 4.2 Handler /setparams
Создать файл: `bot/handlers/admin.py`

**Функционал:**
- Создание нового вебинара
- FSM диалог для сбора информации:
  - Название
  - Описание
  - Дата и время
  - Стоимость
  - Место/ссылка
  - Ссылка на оплату (опционально)
- Сохранение в БД

**FSM States:**
Создать файл: `bot/states/admin.py`
```python
class AdminWebinarStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_date = State()
    waiting_for_price = State()
    waiting_for_location = State()
    waiting_for_payment_link = State()
```

---

### Этап 5: Система напоминаний

#### 5.1 Планировщик задач
Создать файл: `bot/scheduler/tasks.py`

**Функционал:**
- Настройка APScheduler
- Задача проверки напоминаний (каждые 10 минут)
- Отправка напоминаний за 24 часа
- Отправка напоминаний за 1 час
- Обновление флагов в БД

**Пример:**
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def check_24h_reminders(bot):
    # Получить покупки для напоминания
    purchases = await crud.get_purchases_for_reminder(session, 24, "notification_24h_sent")

    for purchase in purchases:
        # Отправить напоминание
        await bot.send_message(
            purchase.user.telegram_id,
            messages.REMINDER_24H.format(...)
        )
        # Пометить как отправлено
        await crud.mark_notification_sent(session, purchase.id, "24h")

scheduler.add_job(
    check_24h_reminders,
    'interval',
    minutes=10,
    args=[bot]
)

scheduler.start()
```

---

### Этап 6: Интеграция с Google Sheets

#### 6.1 Google Sheets Service
Создать файл: `bot/services/google_sheets_service.py`

**Функционал:**
- Подключение к Google Sheets API через Service Account
- Экспорт пользователей
- Экспорт покупок
- Синхронизация (вызывается по расписанию)

**Документация:**
https://docs.gspread.org/

**Пример:**
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheets():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        settings.google_sheets_creds_file, scope
    )
    client = gspread.authorize(creds)
    return client.open_by_key(settings.google_sheet_id)

async def sync_users_to_sheets(session):
    sheet = connect_to_sheets()
    worksheet = sheet.worksheet("Пользователи")

    # Получить всех пользователей
    users = await get_all_users(session)

    # Очистить и записать
    worksheet.clear()
    # ...
```

#### 6.2 Добавить в планировщик
```python
scheduler.add_job(
    sync_to_google_sheets,
    'interval',
    minutes=30,
    args=[session]
)
```

---

### Этап 7: Telegram MiniApp

#### 7.1 Создать React проект
```bash
cd miniapp
npm create vite@latest . -- --template react
npm install @twa-dev/sdk axios react-router-dom
```

#### 7.2 Основные компоненты
- `MainPage.jsx` - анонсы вебинаров
- `ArchivePage.jsx` - купленные вебинары
- `WebinarCard.jsx` - карточка вебинара

#### 7.3 Интеграция с Telegram
```javascript
import WebApp from '@twa-dev/sdk'

// Инициализация
WebApp.ready()

// Получить данные пользователя
const user = WebApp.initDataUnsafe.user

// Отправить данные боту
WebApp.sendData(JSON.stringify({ action: 'purchase', webinar_id: 1 }))
```

#### 7.4 Handler для MiniApp
Создать файл: `bot/handlers/miniapp.py`

**Функционал:**
- Обработка web_app_data
- Парсинг JSON
- Выполнение действий (покупка, просмотр архива)

---

## 📋 Рекомендуемый порядок разработки

1. **Сначала:** Handlers start + middleware подписки
2. **Затем:** Handler вебинар + интеграция с ЮKassa
3. **Потом:** FAQ и поддержка
4. **Далее:** Админ панель
5. **После:** Система напоминаний
6. **В конце:** Google Sheets и MiniApp

---

## 🧪 Тестирование

После каждого этапа:

1. Создайте .env файл с реальными токенами
2. Запустите бота: `python run.py`
3. Протестируйте функционал в Telegram
4. Проверьте логи на ошибки

### Тестовый режим ЮKassa

Используйте тестовый Shop ID для разработки:
https://yookassa.ru/developers/using-api/testing

---

## 📚 Полезные ссылки

- [aiogram 3.x документация](https://docs.aiogram.dev/en/latest/)
- [ЮKassa API](https://yookassa.ru/developers/api)
- [Google Sheets API (gspread)](https://docs.gspread.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram WebApp SDK](https://core.telegram.org/bots/webapps)

---

## 💡 Советы

1. **Используйте логирование:** `logger.info()`, `logger.error()`
2. **Обрабатывайте ошибки:** try/except для всех внешних API
3. **Тестируйте пошагово:** не пишите сразу весь код
4. **Читайте документацию:** особенно aiogram 3.x - он отличается от 2.x
5. **Сохраняйте прогресс:** делайте git commit после каждого этапа

---

**Готовы начать? Начните с Этапа 1!** 🚀
