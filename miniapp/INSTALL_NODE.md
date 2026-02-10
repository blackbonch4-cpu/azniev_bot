# Установка Node.js на macOS

## Способ 1: Официальный установщик (рекомендуется)

1. Скачайте Node.js с https://nodejs.org/
2. Выберите LTS версию (Long Term Support)
3. Запустите установщик
4. После установки откройте новый терминал и проверьте:
```bash
node --version
npm --version
```

## Способ 2: Через Homebrew

Если у вас есть Homebrew:
```bash
brew install node
```

## После установки:

Вернитесь в терминал и запустите:
```bash
cd /Users/blackdany/telegram-webinar-bot/miniapp
npm install
npm run build
npx vercel
```
