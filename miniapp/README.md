# 📱 Telegram MiniApp - Вебинары

Telegram Mini App для просмотра доступных вебинаров и управления покупками.

## 🚀 Быстрый старт

```bash
# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Сборка для production
npm run build
```

## 📁 Структура

```
miniapp/
├── src/
│   ├── api/
│   │   └── api.js              # API запросы к бэкенду
│   ├── components/
│   │   ├── WebinarCard.jsx     # Карточка вебинара
│   │   └── WebinarCard.css
│   ├── pages/
│   │   └── MainPage.jsx        # Главная страница со списком
│   ├── App.jsx                 # Главный компонент
│   ├── App.css
│   └── main.jsx                # Точка входа
├── index.html
├── package.json
└── vite.config.js
```

## 🔧 Настройка

1. Создайте `.env` файл:
```env
VITE_API_URL=https://your-api-url.com/api
```

2. Настройте BotFather:
```
/newapp
/setappmenubutton - добавить кнопку в меню бота
```

3. Разместите собранное приложение на хостинге

## 📦 Функционал

- 🎓 Список всех вебинаров
- ✅ Отметка купленных вебинаров
- 👥 Прямой переход в группу вебинара
- 🎨 Адаптация под тему Telegram
- 📱 Полная интеграция с Telegram WebApp SDK

## 🎨 Особенности

- Использует цвета темы Telegram
- Адаптивный дизайн
- Оптимизирован для мобильных устройств
- Быстрая загрузка

## 🛠️ Технологии

- React 18
- Vite
- Telegram WebApp SDK (@twa-dev/sdk)
- Axios для API запросов
