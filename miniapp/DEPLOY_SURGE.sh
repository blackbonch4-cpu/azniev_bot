#!/bin/bash

# Деплой на Surge.sh
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

cd /Users/blackdany/telegram-webinar-bot/miniapp

# Обновить vite.config.js для корневого пути
cat > vite.config.js << 'VITE_EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    port: 3000,
    host: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
VITE_EOF

# Собрать проект
npm run build

# Деплой на Surge
cd dist
surge --domain azniev-webinar.surge.sh

