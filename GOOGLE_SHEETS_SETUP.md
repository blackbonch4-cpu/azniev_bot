# Настройка Google Sheets

## 1. Service Account (обязательно)

1. Откройте https://console.cloud.google.com/
2. IAM & Admin → Service Accounts → CREATE SERVICE ACCOUNT
3. Имя: `telegram-bot-sheets`
4. После создания: Keys → ADD KEY → JSON
5. Скачанный файл переименуйте в `credentials.json`
6. Положите в корень проекта: `/Users/blackdany/telegram-webinar-bot/credentials.json`

## 2. Включите APIs

В Google Cloud Console:
- APIs & Services → Enable APIs
- Включите:
  - Google Sheets API
  - Google Drive API

## 3. Дайте доступ к таблице

1. Откройте ваш credentials.json
2. Найдите поле "client_email" (например: bot@project.iam.gserviceaccount.com)
3. Откройте вашу Google Таблицу
4. Нажмите "Поделиться"
5. Добавьте этот email
6. Дайте права "Редактор"

## 4. Готово!

Перезапустите бота - синхронизация заработает автоматически.
