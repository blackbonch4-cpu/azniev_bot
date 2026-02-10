#!/usr/bin/env python3
"""
Скрипт для быстрого запуска бота

Использование:
    python run.py
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.main import main
import asyncio

if __name__ == "__main__":
    print("🚀 Запуск Telegram бота...")
    print("Для остановки нажмите Ctrl+C")
    print("-" * 50)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка при запуске: {e}")
        sys.exit(1)
