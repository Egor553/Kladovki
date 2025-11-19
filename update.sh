#!/bin/bash

# Скрипт для автоматического обновления бота на сервере
# Этот скрипт можно вызвать вручную или через webhook/GitHub Actions

set -e  # Остановка при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Начинаем обновление бота...${NC}"

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Проверяем, что мы в git репозитории
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Ошибка: директория не является git репозиторием${NC}"
    exit 1
fi

# Сохраняем текущую ветку
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${GREEN}📦 Текущая ветка: $CURRENT_BRANCH${NC}"

# Получаем последние изменения
echo -e "${YELLOW}⬇️  Получаем обновления с GitHub...${NC}"
git fetch origin

# Проверяем, есть ли изменения
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${GREEN}✅ Код уже актуален, обновлений нет${NC}"
    exit 0
fi

# Делаем backup текущей версии (опционально)
echo -e "${YELLOW}💾 Создаем резервную копию...${NC}"
BACKUP_DIR="../udobnysklad_backup_$(date +%Y%m%d_%H%M%S)"
cp -r . "$BACKUP_DIR" 2>/dev/null || true

# Обновляем код
echo -e "${YELLOW}🔄 Обновляем код...${NC}"
git pull origin "$CURRENT_BRANCH"

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ Виртуальное окружение не найдено!${NC}"
    exit 1
fi

# Обновляем зависимости
echo -e "${YELLOW}📦 Обновляем зависимости...${NC}"
pip install -r requirements.txt --quiet --upgrade

# Перезапускаем сервис
echo -e "${YELLOW}🔄 Перезапускаем бота...${NC}"
if systemctl is-active --quiet udobnysklad.service; then
    sudo systemctl restart udobnysklad.service
    echo -e "${GREEN}✅ Бот перезапущен${NC}"
else
    echo -e "${YELLOW}⚠️  Сервис не запущен, запускаем...${NC}"
    sudo systemctl start udobnysklad.service
fi

# Проверяем статус
sleep 2
if systemctl is-active --quiet udobnysklad.service; then
    echo -e "${GREEN}✅ Обновление завершено успешно!${NC}"
    echo -e "${GREEN}📊 Статус сервиса:${NC}"
    sudo systemctl status udobnysklad.service --no-pager -l
else
    echo -e "${RED}❌ Ошибка: сервис не запустился после обновления${NC}"
    echo -e "${YELLOW}💡 Проверьте логи: sudo journalctl -u udobnysklad.service -n 50${NC}"
    exit 1
fi

