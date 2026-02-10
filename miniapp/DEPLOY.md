# Деплой MiniApp

## Вариант 1: Vercel (рекомендуется)

### Быстрый способ:

1. Установите Vercel CLI:
```bash
npm install -g vercel
```

2. Перейдите в директорию miniapp:
```bash
cd /Users/blackdany/telegram-webinar-bot/miniapp
```

3. Создайте production .env:
```bash
echo "VITE_API_URL=https://your-bot-api.com/api" > .env.production
```

4. Запустите деплой:
```bash
vercel
```

5. Следуйте инструкциям:
   - Login в Vercel (через GitHub)
   - Set up and deploy: Yes
   - Which scope: ваш аккаунт
   - Link to existing project: No
   - Project name: telegram-webinar-miniapp
   - Directory: ./
   - Override settings: No

6. После деплоя получите URL типа:
   `https://telegram-webinar-miniapp.vercel.app`

7. **Этот URL вставьте в BotFather**

---

## Вариант 2: GitHub Pages (бесплатно)

1. Создайте GitHub репозиторий

2. Обновите vite.config.js:
```js
export default defineConfig({
  base: '/your-repo-name/',
  // ...
})
```

3. Добавьте в package.json:
```json
{
  "scripts": {
    "deploy": "npm run build && gh-pages -d dist"
  }
}
```

4. Установите gh-pages:
```bash
npm install --save-dev gh-pages
```

5. Деплой:
```bash
npm run deploy
```

6. URL: `https://yourusername.github.io/your-repo-name/`

---

## Вариант 3: Netlify (тоже простой)

1. Перетащите папку `dist` на https://app.netlify.com/drop

2. Получите URL типа: `https://random-name.netlify.app`

---

## После деплоя:

1. Скопируйте URL
2. Откройте @BotFather
3. Отправьте ваш URL (например: `https://telegram-webinar-miniapp.vercel.app`)
4. Готово! ✅
