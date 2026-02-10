# Настройка GitHub для деплоя

## Проблема
GitHub требует авторизацию для push.

## Решения:

### 1. Создать Personal Access Token (рекомендуется)

1. Откройте https://github.com/settings/tokens
2. Нажмите **Generate new token (classic)**
3. Выберите scopes: `repo` (полный доступ к репозиториям)
4. Скопируйте токен

5. В терминале выполните:
```bash
git remote set-url origin https://TOKEN@github.com/blackbonch4-cpu/azniev_bot.git
```
Замените TOKEN на ваш токен.

6. Попробуйте снова:
```bash
cd /Users/blackdany/telegram-webinar-bot/miniapp
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
npm run deploy
```

---

### 2. Netlify (проще всего!)

Без GitHub вообще:
1. Откройте https://app.netlify.com/drop
2. Перетащите папку `/Users/blackdany/telegram-webinar-bot/miniapp/dist`
3. Получите URL
4. Готово!

