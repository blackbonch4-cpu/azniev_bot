import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import WebApp from '@twa-dev/sdk'

// Инициализация Telegram WebApp
WebApp.ready()
WebApp.expand()

// Устанавливаем цвета темы
document.body.style.backgroundColor = WebApp.themeParams.bg_color || '#ffffff'
document.body.style.color = WebApp.themeParams.text_color || '#000000'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
