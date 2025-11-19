#!/bin/bash

# Скрипт для настройки автоматического обновления через GitHub API

set -e

echo "🔧 Настройка автоматического обновления через GitHub API..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Проверяем наличие виртуального окружения, создаем если нет
if [ ! -d "venv" ]; then
    echo "📦 Виртуальное окружение не найдено, создаем..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
fi

# Активируем venv
source venv/bin/activate

# Обновляем pip
echo "📦 Обновляем pip..."
pip install --upgrade pip --quiet

# Устанавливаем все зависимости
echo "📦 Устанавливаем зависимости..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
else
    echo "⚠️  Файл requirements.txt не найден, устанавливаем только requests"
    pip install requests --quiet
fi

# Делаем скрипт исполняемым
chmod +x auto_update.py

# Копируем service файл
echo "📋 Настраиваем systemd timer..."
sudo cp auto_update.service /etc/systemd/system/

# Создаем timer файл для периодического запуска
sudo tee /etc/systemd/system/auto_update.timer > /dev/null <<EOF
[Unit]
Description=Auto Update Timer for Udobnysklad Bot
Requires=auto_update.service

[Timer]
# Проверка каждые 5 минут
OnBootSec=2min
OnUnitActiveSec=5min
Unit=auto_update.service

[Install]
WantedBy=timers.target
EOF

# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем и запускаем timer
sudo systemctl enable auto_update.timer
sudo systemctl start auto_update.timer

# Проверяем статус
echo ""
echo "✅ Автоматическое обновление настроено!"
echo ""
echo "📊 Статус:"
sudo systemctl status auto_update.timer --no-pager -l

echo ""
echo "📝 Полезные команды:"
echo "  Проверить статус: sudo systemctl status auto_update.timer"
echo "  Посмотреть логи: sudo journalctl -u auto_update.service -f"
echo "  Запустить обновление вручную: sudo systemctl start auto_update.service"
echo "  Остановить автообновление: sudo systemctl stop auto_update.timer"

