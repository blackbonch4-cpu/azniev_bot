# Варианты деплоя MiniApp

## 1. Netlify (самый простой) ⭐

### Вариант A: Drag & Drop
1. Откройте https://app.netlify.com/drop
2. Перетащите папку `miniapp/dist` 
3. Готово! Получите URL

### Вариант B: CLI
```bash
cd /Users/blackdany/telegram-webinar-bot/miniapp
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

---

## 2. GitHub Pages (бесплатно навсегда)

```bash
cd /Users/blackdany/telegram-webinar-bot/miniapp

# Установить gh-pages
npm install --save-dev gh-pages

# Добавить в package.json scripts:
# "deploy": "vite build && gh-pages -d dist"

# Деплой
npm run deploy
```

URL: `https://your-username.github.io/repo-name/`

---

## 3. Cloudflare Pages (быстрый)

1. Откройте https://pages.cloudflare.com/
2. Подключите GitHub репозиторий
3. Build command: `npm run build`
4. Output directory: `dist`
5. Deploy!

---

## 4. Surge.sh (один терминал команда)

```bash
npm install -g surge
cd /Users/blackdany/telegram-webinar-bot/miniapp/dist
surge
```

Введите email и домен (или автогенерация).
URL: `https://your-name.surge.sh`

---

## 5. Vercel (автоматические обновления)

```bash
cd /Users/blackdany/telegram-webinar-bot/miniapp
npm install -g vercel
vercel
```

---

## Рекомендации:

- **Самый простой**: Netlify Drag & Drop
- **Лучшая интеграция с GitHub**: GitHub Pages / Cloudflare Pages
- **Самый быстрый**: Surge.sh (1 команда)
- **Автообновления при push**: Vercel / Netlify / Cloudflare

