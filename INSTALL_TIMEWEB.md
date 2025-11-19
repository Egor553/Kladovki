# 📋 Пошаговая инструкция: Настройка автообновления на Timeweb

## Шаг 1: Подключение к серверу Timeweb

1. Зайдите в панель управления Timeweb
2. Найдите раздел "SSH доступ" или "Консоль"
3. Откройте SSH консоль (или используйте программу PuTTY/Windows Terminal)

## Шаг 2: Переход в директорию проекта

Введите в консоль:

```bash
cd /root/udobnysklad
```

Если папки нет, сначала клонируйте репозиторий:

```bash
cd /root
git clone https://github.com/Kladovki/udobnysklad.git
cd udobnysklad
```

## Шаг 3: Проверка файлов

Убедитесь, что все файлы на месте:

```bash
ls -la
```

Должны быть видны файлы: `auto_update.py`, `setup_auto_update.sh`, `requirements.txt` и другие.

## Шаг 4: Настройка виртуального окружения (если еще не сделано)

```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем его
source venv/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

## Шаг 5: Настройка автообновления

Сделайте скрипт исполняемым и запустите его:

```bash
chmod +x setup_auto_update.sh
./setup_auto_update.sh
```

Скрипт автоматически:
- Установит недостающие зависимости
- Настроит systemd timer
- Включит автоматическую проверку обновлений каждые 5 минут

## Шаг 6: Проверка работы

Проверьте, что все работает:

```bash
# Проверить статус автообновления
sudo systemctl status auto_update.timer

# Посмотреть логи (если нужно)
sudo journalctl -u auto_update.service -n 20
```

## Готово! ✅

Теперь при каждом изменении кода на GitHub, он автоматически обновится на сервере в течение 5 минут.

---

## 🔧 Полезные команды для управления

### Проверить статус автообновления:
```bash
sudo systemctl status auto_update.timer
```

### Посмотреть последние логи:
```bash
sudo journalctl -u auto_update.service -f
```

### Запустить обновление вручную прямо сейчас:
```bash
sudo systemctl start auto_update.service
```

### Остановить автообновление:
```bash
sudo systemctl stop auto_update.timer
```

### Включить автообновление обратно:
```bash
sudo systemctl start auto_update.timer
```

---

## ❓ Если что-то пошло не так

### Проблема: "command not found: python3"
**Решение:**
```bash
# Установите Python
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### Проблема: "git: command not found"
**Решение:**
```bash
# Установите Git
sudo apt update
sudo apt install git -y
```

### Проблема: "Permission denied"
**Решение:**
```bash
# Убедитесь, что вы используете sudo для systemd команд
# Или проверьте права доступа к файлам
chmod +x setup_auto_update.sh
chmod +x auto_update.py
```

### Проблема: Скрипт не находит файлы
**Решение:**
```bash
# Убедитесь, что вы в правильной директории
pwd  # Должно показать /root/udobnysklad
ls -la  # Проверьте наличие файлов
```

---

## 📝 Полная последовательность команд (копируйте по порядку)

```bash
# 1. Переход в директорию проекта
cd /root/udobnysklad

# 2. Если папки нет - клонируем репозиторий
# cd /root
# git clone https://github.com/Kladovki/udobnysklad.git
# cd udobnysklad

# 3. Создаем/активируем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 4. Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt

# 5. Настраиваем автообновление
chmod +x setup_auto_update.sh
./setup_auto_update.sh

# 6. Проверяем статус
sudo systemctl status auto_update.timer
```

Готово! 🎉

