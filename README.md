# Удобный Склад - Telegram Bot

Telegram бот для аренды складских помещений в Челябинской области.

## 🚀 Быстрый старт

### Требования
- Python 3.9+
- Telegram Bot Token (получить у @BotFather)

### Установка локально

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Kladovki/udobnysklad.git
cd udobnysklad
```

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env`:
```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваш BOT_TOKEN и ADMIN_CHAT_ID
```

5. Запустите бота:
```bash
python main.py
```

## 📦 Деплой на Timeweb (VPS)

### Шаг 1: Подготовка сервера

1. Подключитесь к вашему VPS серверу через SSH
2. Установите Python 3.9+ и необходимые пакеты:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y
```

### Шаг 2: Клонирование репозитория

```bash
cd /root  # или в другую директорию по вашему выбору
git clone https://github.com/Kladovki/udobnysklad.git
cd udobnysklad
```

### Шаг 3: Настройка окружения

1. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Установите зависимости:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Создайте файл `.env`:
```bash
nano .env
```

Добавьте в файл:
```
BOT_TOKEN=ваш_токен_бота
ADMIN_CHAT_ID=ваш_админ_чат_id
```

Сохраните файл (Ctrl+O, Enter, Ctrl+X)

### Шаг 4: Настройка автозапуска через systemd

1. Скопируйте service файл:
```bash
sudo cp udobnysklad.service /etc/systemd/system/
```

2. Отредактируйте пути в service файле (если нужно):
```bash
sudo nano /etc/systemd/system/udobnysklad.service
```

Измените пути:
- `WorkingDirectory` - путь к директории проекта
- `ExecStart` - путь к Python в venv и путь к main.py
- `User` - ваш пользователь (или оставьте root)

3. Перезагрузите systemd:
```bash
sudo systemctl daemon-reload
```

4. Включите автозапуск:
```bash
sudo systemctl enable udobnysklad.service
```

5. Запустите сервис:
```bash
sudo systemctl start udobnysklad.service
```

6. Проверьте статус:
```bash
sudo systemctl status udobnysklad.service
```

### Полезные команды для управления ботом

```bash
# Остановить бота
sudo systemctl stop udobnysklad.service

# Запустить бота
sudo systemctl start udobnysklad.service

# Перезапустить бота
sudo systemctl restart udobnysklad.service

# Посмотреть логи
sudo journalctl -u udobnysklad.service -f

# Отключить автозапуск
sudo systemctl disable udobnysklad.service
```

### Альтернативный способ: Запуск через screen/tmux

Если не хотите использовать systemd, можно запустить бота через screen:

```bash
# Установите screen
sudo apt install screen -y

# Создайте новую сессию
screen -S bot

# Активируйте venv и запустите бота
cd /root/udobnysklad
source venv/bin/activate
python3 main.py

# Отключитесь от сессии: Ctrl+A, затем D
# Вернуться к сессии: screen -r bot
```

## 🔧 Настройка

### Переменные окружения

- `BOT_TOKEN` - токен бота от @BotFather (обязательно)
- `ADMIN_CHAT_ID` - ID чата для получения заявок (обязательно)

### Файл proxies.txt

Если нужно использовать прокси, создайте файл `proxies.txt` в корне проекта и добавьте прокси в формате:
```
http://user:pass@host:port
socks5://user:pass@host:port
```

## 📝 Структура проекта

```
udobnysklad/
├── main.py                  # Точка входа
├── bot.py                   # Основная логика бота
├── config.py                # Конфигурация и настройки
├── database.py              # Работа с базой данных
├── handlers.py              # Обработчики команд
├── profile_handlers.py      # Обработчики профиля
├── keyboards.py             # Клавиатуры
├── setup_bot.py             # Настройка бота
├── requirements.txt         # Зависимости
├── start.sh                 # Скрипт запуска
├── update.sh                # Скрипт автоматического обновления
├── auto_update.py           # Скрипт автообновления через GitHub API
├── auto_update.service      # Systemd service для автообновления
├── setup_auto_update.sh     # Скрипт настройки автообновления
├── webhook_server.py        # Webhook сервер для автообновления
├── udobnysklad.service      # Systemd service файл
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions для автообновления
└── README.md                # Этот файл
```

## 🐛 Решение проблем

### Бот не запускается

1. Проверьте, что файл `.env` существует и содержит правильные значения
2. Проверьте логи: `sudo journalctl -u udobnysklad.service -n 50`
3. Убедитесь, что Python и все зависимости установлены

### Ошибки с прокси

Если возникают проблемы с прокси, бот автоматически переключится на прямое подключение после 3 неудачных попыток.

### Обновление кода

#### Ручное обновление

```bash
cd /root/udobnysklad
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart udobnysklad.service
```

#### Автоматическое обновление через GitHub Actions

При каждом push в репозиторий код автоматически обновится на сервере!

**Настройка:**

1. **На сервере Timeweb:**
   - Убедитесь, что у вас есть SSH ключ для доступа к серверу
   - Если нет, создайте его:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions"
   # Скопируйте публичный ключ в authorized_keys
   cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
   ```

2. **На GitHub:**
   - Перейдите в Settings → Secrets and variables → Actions
   - Добавьте следующие секреты:
     - `TIMEWEB_HOST` - IP адрес или домен вашего сервера
     - `TIMEWEB_USER` - имя пользователя для SSH (обычно `root`)
     - `TIMEWEB_SSH_KEY` - приватный SSH ключ (содержимое файла `~/.ssh/id_rsa`)
     - `TIMEWEB_PORT` - порт SSH (обычно `22`, можно не указывать)

3. **Готово!** Теперь при каждом push в ветку `main` код автоматически обновится на сервере.

#### Автоматическое обновление через Webhook (альтернативный способ)

Если GitHub Actions не подходит, можно использовать webhook:

1. **На сервере запустите webhook сервер:**
   ```bash
   cd /root/udobnysklad
   source venv/bin/activate
   pip install flask  # или используйте встроенный webhook_server.py
   
   # Создайте файл .env и добавьте:
   # WEBHOOK_SECRET=ваш_секретный_ключ
   # PROJECT_DIR=/root/udobnysklad
   # WEBHOOK_PORT=8080
   
   # Запустите webhook сервер
   python3 webhook_server.py
   ```

2. **Настройте GitHub Webhook:**
   - Перейдите в Settings → Webhooks → Add webhook
   - Payload URL: `http://ваш_сервер_ip:8080/webhook`
   - Content type: `application/json`
   - Secret: ваш секретный ключ (тот же, что в .env)
   - Events: выберите "Just the push event"
   - Active: включите

3. **Сделайте webhook сервер автозапускаемым:**
   ```bash
   # Создайте systemd service для webhook
   sudo nano /etc/systemd/system/webhook.service
   ```
   
   Добавьте:
   ```ini
   [Unit]
   Description=GitHub Webhook Server
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/udobnysklad
   Environment="PATH=/root/udobnysklad/venv/bin"
   ExecStart=/root/udobnysklad/venv/bin/python3 /root/udobnysklad/webhook_server.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Запустите:
   ```bash
   sudo systemctl enable webhook.service
   sudo systemctl start webhook.service
   ```

#### Автоматическое обновление через GitHub API (самый простой способ!)

Этот способ не требует настройки SSH ключей или webhook - просто проверяет GitHub API и обновляет код автоматически.

**Настройка:**

1. **На сервере Timeweb запустите скрипт настройки:**
   ```bash
   cd /root/udobnysklad
   chmod +x setup_auto_update.sh
   ./setup_auto_update.sh
   ```

2. **Готово!** Теперь каждые 5 минут скрипт будет проверять наличие обновлений на GitHub и автоматически обновлять код.

**Как это работает:**
- Скрипт `auto_update.py` проверяет последний коммит через GitHub API
- Сравнивает с локальным хешем
- Если есть изменения - делает `git pull`, обновляет зависимости и перезапускает бота
- Работает через systemd timer (проверка каждые 5 минут)

**Управление:**
```bash
# Проверить статус автообновления
sudo systemctl status auto_update.timer

# Посмотреть логи
sudo journalctl -u auto_update.service -f

# Запустить обновление вручную
sudo systemctl start auto_update.service

# Остановить автообновление
sudo systemctl stop auto_update.timer

# Включить автообновление
sudo systemctl start auto_update.timer
```

**Настройка интервала проверки:**

Если хотите изменить интервал проверки (например, каждые 10 минут), отредактируйте файл:
```bash
sudo nano /etc/systemd/system/auto_update.timer
```

Измените строку:
```ini
OnUnitActiveSec=5min  # на нужное значение (например, 10min, 1h)
```

Затем перезагрузите:
```bash
sudo systemctl daemon-reload
sudo systemctl restart auto_update.timer
```

#### Ручной запуск скрипта обновления

Вы также можете запустить скрипт обновления вручную:

```bash
cd /root/udobnysklad
chmod +x update.sh
./update.sh
```

Или через Python скрипт:
```bash
cd /root/udobnysklad
source venv/bin/activate
python3 auto_update.py
```

Этот скрипт:
- Проверит наличие обновлений через GitHub API
- Обновит код
- Обновит зависимости
- Перезапустит бота

## 📞 Поддержка

При возникновении проблем проверьте логи бота и убедитесь, что все переменные окружения настроены правильно.

