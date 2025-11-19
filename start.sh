#!/bin/bash

# Скрипт для запуска Telegram бота на сервере

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Активируем виртуальное окружение (если используется)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Устанавливаем зависимости (если нужно)
if [ ! -d "venv" ]; then
    echo "Создаем виртуальное окружение..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  ВНИМАНИЕ: Файл .env не найден!"
    echo "Создайте файл .env на основе .env.example"
    exit 1
fi

# Запускаем бота
echo "🚀 Запуск бота..."
python3 main.py

