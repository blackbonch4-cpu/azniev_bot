# 🎓 Telegram Бот для управления вебинарами

Полнофункциональный Telegram бот для управления базой клиентов, регистрации на вебинары, приема оплаты и отправки уведомлений.

## ✨ Основной функционал

- ✅ Проверка подписки на приватный канал
- 📧 Регистрация пользователей с валидацией email
- 💾 Хранение данных в SQLite + синхронизация с Google Sheets
- 💳 Гибридная система оплаты (ЮKassa API + ручные ссылки)
- ⏰ Автоматические напоминания (за 24 часа и за 1 час)
- 💬 FAQ система с inline меню
- 🆘 Система поддержки (отправка вопросов в супергруппу)
- ⚙️ Админ панель для управления событиями
- 📱 MiniApp как личный кабинет пользователя (в разработке)

## 🗂️ Структура проекта

```
telegram-webinar-bot/
├── bot/
│   ├── handlers/          # Обработчики команд
│   ├── middlewares/       # Промежуточные обработчики
│   ├── states/            # FSM состояния
│   ├── database/          # Модели и работа с БД
│   ├── services/          # Бизнес-логика
│   ├── utils/             # Утилиты
│   ├── texts/             # Все текстовки бота
│   ├── scheduler/         # Планировщик задач
│   ├── config.py          # Конфигурация
│   └── main.py            # Точка входа
├── miniapp/               # Telegram MiniApp
├── api/                   # Backend API для MiniApp
├── requirements.txt       # Python зависимости
├── .env.example           # Пример переменных окружения
└── README.md              # Этот файл
```

## 🚀 Быстрый старт

### 1. Предварительные требования

- Python 3.10 или выше
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- Приватный канал/группа в Telegram
- Google Cloud проект с доступом к Sheets API (опционально)
- Аккаунт ЮKassa для приема платежей (опционально)

### 2. Установка

```bash
# Клонируйте репозиторий или скачайте файлы
cd telegram-webinar-bot

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
# На macOS/Linux:
source venv/bin/activate
# На Windows:
# venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
```

### 3. Настройка

#### 3.1 Создайте файл `.env`

```bash
cp .env.example .env
```

#### 3.2 Заполните переменные окружения в `.env`

```env
# Основные настройки
BOT_TOKEN=your_bot_token_here
CHANNEL_ID=-1001234567890
ADMIN_IDS=123456789,987654321

# Поддержка
SUPPORT_GROUP_ID=-1001234567890
SUPPORT_TOPIC_ID=1

# ЮKassa (опционально)
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# Google Sheets (опционально)
GOOGLE_SHEETS_CREDS_FILE=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id
```

#### 3.3 Получение необходимых ID

**Telegram ID пользователя:**
- Напишите [@username_to_id_bot](https://t.me/username_to_id_bot)
- Отправьте `/start` и получите свой ID

**ID канала/группы:**
1. Добавьте [@username_to_id_bot](https://t.me/username_to_id_bot) в ваш канал/группу как администратора
2. Бот отправит ID канала/группы (например: `-1001234567890`)
3. Удалите бота из канала после получения ID

**ID темы в супергруппе (для поддержки):**
- Откройте тему в супергруппе
- ID будет в URL: `https://t.me/c/1234567890/1` (последняя цифра - ID темы)

### 4. Настройка бота для приватного канала

Чтобы бот мог проверять подписку на приватный канал:

1. Добавьте бота в приватный канал как **администратора**
2. Дайте боту права:
   - ✅ "Просмотр сообщений" (обязательно)
   - ✅ "Добавление участников" (рекомендуется)

### 5. Настройка Google Sheets (опционально)

Если хотите использовать синхронизацию с Google Sheets:

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект
3. Включите Google Sheets API
4. Создайте Service Account
5. Скачайте JSON ключ и сохраните как `credentials.json` в корне проекта
6. Создайте Google Таблицу и дайте доступ Service Account (email из JSON)
7. Скопируйте ID таблицы из URL и вставьте в `.env`

### 6. Настройка ЮKassa (опционально)

Для автоматического приема платежей:

1. Зарегистрируйтесь на [ЮKassa](https://yookassa.ru/)
2. Получите Shop ID и Secret Key в личном кабинете
3. Вставьте их в `.env`
4. Настройте webhook для уведомлений о платежах (если используете)

## 🎯 Запуск бота

### Локальный запуск

```bash
# Активируйте виртуальное окружение
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Запустите бота
python -m bot.main
```

Бот запустится в режиме polling (постоянно опрашивает Telegram API).

### Запуск на VPS (Beget)

#### 1. Подготовка сервера

```bash
# Подключитесь к серверу по SSH
ssh username@your-server.com

# Установите Python 3.10+ (если нет)
# На Beget обычно уже установлен

# Создайте директорию для проекта
mkdir ~/telegram-webinar-bot
cd ~/telegram-webinar-bot

# Загрузите файлы проекта
# Можно использовать git, scp или FTP
```

#### 2. Установка зависимостей

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

#### 3. Настройка автозапуска (systemd)

Создайте файл `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Webinar Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/telegram-webinar-bot
Environment="PATH=/home/your_username/telegram-webinar-bot/venv/bin"
ExecStart=/home/your_username/telegram-webinar-bot/venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Проверка статуса
sudo systemctl status telegram-bot

# Просмотр логов
sudo journalctl -u telegram-bot -f
```

## 📝 Редактирование текстов бота

Все тексты бота находятся в файле [bot/texts/messages.py](bot/texts/messages.py).

Вы можете свободно редактировать любые тексты, добавлять смайлы и форматирование.

**Пример:**

```python
WELCOME_NEW_USER = """👋 Привет, {first_name}!

Добро пожаловать в наш бот!
"""
```

Поддерживается Markdown разметка Telegram:
- `**жирный текст**`
- `*курсив*`
- `__подчеркнутый__`
- `~~зачеркнутый~~`
- `` `моноширинный` ``
- ```многострочный код```

## 🛠️ Разработка

### Следующие шаги разработки

Текущая версия содержит базовую структуру проекта. Необходимо реализовать:

1. **Handlers (обработчики команд)**
   - `bot/handlers/start.py` - регистрация и /start
   - `bot/handlers/webinar.py` - команда "Вебинар"
   - `bot/handlers/support.py` - /help и FAQ
   - `bot/handlers/admin.py` - /setparams и админ панель
   - `bot/handlers/payments.py` - обработка платежей

2. **Middlewares**
   - `bot/middlewares/subscription_check.py` - проверка подписки
   - `bot/middlewares/registration_check.py` - проверка регистрации
   - `bot/middlewares/admin_check.py` - проверка прав админа

3. **States (FSM состояния)**
   - `bot/states/registration.py` - состояния регистрации
   - `bot/states/support.py` - состояния вопросов
   - `bot/states/admin.py` - состояния админ панели

4. **Services (сервисы)**
   - `bot/services/payment_service.py` - интеграция с ЮKassa
   - `bot/services/notification_service.py` - напоминания
   - `bot/services/google_sheets_service.py` - синхронизация с Sheets
   - `bot/services/subscription_service.py` - проверка подписки

5. **Scheduler (планировщик)**
   - `bot/scheduler/tasks.py` - задачи для напоминаний

6. **MiniApp (веб-приложение)**
   - Разработка React приложения
   - Интеграция с Telegram WebApp SDK

### Структура базы данных

База данных создается автоматически при первом запуске.

**Таблицы:**
- `users` - пользователи
- `webinars` - вебинары
- `purchases` - покупки/участия
- `faq_questions` - FAQ вопросы
- `support_tickets` - вопросы в поддержку

Подробнее см. [bot/database/models.py](bot/database/models.py)

## 📊 Мониторинг и логи

Логи записываются в stdout. Уровень логирования настраивается в `.env`:

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

При запуске через systemd логи доступны через journalctl:

```bash
# Просмотр последних логов
sudo journalctl -u telegram-bot -n 100

# Следить за логами в реальном времени
sudo journalctl -u telegram-bot -f
```

## 🔒 Безопасность

- ❗ Никогда не коммитьте файл `.env` в git
- ❗ Храните `credentials.json` в безопасности
- ❗ Регулярно обновляйте токены и ключи
- ❗ Используйте сильные пароли для VPS
- ✅ Используйте SSH ключи для доступа к серверу
- ✅ Настройте firewall на сервере

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте логи бота
2. Убедитесь что все переменные в `.env` заполнены корректно
3. Проверьте что бот добавлен в канал как администратор
4. Убедитесь что все зависимости установлены

## 📄 Лицензия

Этот проект создан для личного использования.

## 🎯 Roadmap

- [x] Базовая структура проекта
- [x] Модели базы данных
- [x] Конфигурация и валидаторы
- [ ] Handlers (регистрация, вебинары, поддержка, админ)
- [ ] Middlewares (проверка подписки и регистрации)
- [ ] Интеграция с ЮKassa
- [ ] Интеграция с Google Sheets
- [ ] Система напоминаний
- [ ] MiniApp (личный кабинет)
- [ ] Геймификация
- [ ] Расширенная аналитика

---

**Создано с ❤️ для управления вебинарами**
