"""
Скрипт для автоматического обновления бота через GitHub API
Проверяет последний коммит и обновляет код при изменениях
"""
import subprocess
import requests
import json
import os
import logging
from pathlib import Path
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Настройки
GITHUB_REPO = os.getenv("GITHUB_REPO", "Kladovki/udobnysklad")  # владелец/репозиторий
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
PROJECT_DIR = os.getenv("PROJECT_DIR", "/root/udobnysklad")
COMMIT_HASH_FILE = Path(PROJECT_DIR) / ".last_commit_hash"


def get_latest_commit_hash():
    """Получить хеш последнего коммита через GitHub API"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["sha"]
    except Exception as e:
        logger.error(f"Ошибка при получении последнего коммита: {e}")
        return None


def get_local_commit_hash():
    """Получить хеш последнего коммита локально"""
    try:
        if COMMIT_HASH_FILE.exists():
            return COMMIT_HASH_FILE.read_text().strip()
        return None
    except Exception as e:
        logger.error(f"Ошибка при чтении локального хеша: {e}")
        return None


def save_local_commit_hash(commit_hash):
    """Сохранить хеш последнего коммита"""
    try:
        COMMIT_HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
        COMMIT_HASH_FILE.write_text(commit_hash)
    except Exception as e:
        logger.error(f"Ошибка при сохранении хеша: {e}")


def update_code():
    """Обновить код через git pull"""
    try:
        logger.info("🔄 Начинаем обновление кода...")
        
        # Переходим в директорию проекта
        os.chdir(PROJECT_DIR)
        
        # Получаем последний коммит перед обновлением
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10
        )
        old_hash = result.stdout.strip() if result.returncode == 0 else None
        
        # Делаем git pull
        result = subprocess.run(
            ["git", "pull", "origin", GITHUB_BRANCH],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Ошибка при git pull: {result.stderr}")
            return False
        
        # Проверяем, были ли изменения
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10
        )
        new_hash = result.stdout.strip() if result.returncode == 0 else None
        
        if old_hash == new_hash:
            logger.info("ℹ️  Изменений нет, код уже актуален")
            return False
        
        logger.info(f"✅ Код обновлен: {old_hash[:7]} → {new_hash[:7]}")
        
        # Обновляем зависимости
        logger.info("📦 Обновляем зависимости...")
        venv_python = Path(PROJECT_DIR) / "venv" / "bin" / "python3"
        if venv_python.exists():
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "-r", "requirements.txt", "--quiet", "--upgrade"],
                cwd=PROJECT_DIR,
                timeout=300
            )
            if result.returncode == 0:
                logger.info("✅ Зависимости обновлены")
            else:
                logger.warning("⚠️  Предупреждение при обновлении зависимостей")
        
        # Перезапускаем сервис
        logger.info("🔄 Перезапускаем бота...")
        result = subprocess.run(
            ["sudo", "systemctl", "restart", "udobnysklad.service"],
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info("✅ Бот перезапущен успешно")
            # Сохраняем новый хеш
            if new_hash:
                save_local_commit_hash(new_hash)
            return True
        else:
            logger.error("❌ Ошибка при перезапуске бота")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Таймаут при обновлении")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении: {e}")
        return False


def main():
    """Основная функция проверки и обновления"""
    logger.info("🔍 Проверяем наличие обновлений...")
    
    # Получаем последний коммит с GitHub
    latest_hash = get_latest_commit_hash()
    if not latest_hash:
        logger.warning("⚠️  Не удалось получить информацию о последнем коммите")
        return
    
    # Получаем локальный хеш
    local_hash = get_local_commit_hash()
    
    # Если локального хеша нет, сохраняем текущий
    if not local_hash:
        logger.info("ℹ️  Первый запуск, сохраняем текущий коммит")
        save_local_commit_hash(latest_hash)
        return
    
    # Сравниваем хеши
    if latest_hash == local_hash:
        logger.info("✅ Код актуален, обновлений нет")
        return
    
    logger.info(f"🆕 Найдены обновления: {local_hash[:7]} → {latest_hash[:7]}")
    
    # Обновляем код
    if update_code():
        logger.info("🎉 Обновление завершено успешно!")
    else:
        logger.error("❌ Ошибка при обновлении")


if __name__ == "__main__":
    main()

