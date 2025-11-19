"""
Простой webhook сервер для автоматического обновления бота
Запустите этот скрипт на сервере для получения уведомлений от GitHub
"""
import subprocess
import hmac
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Секретный ключ для webhook (установите через переменную окружения)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_secret_key_here")
PROJECT_DIR = os.getenv("PROJECT_DIR", "/root/udobnysklad")
PORT = int(os.getenv("WEBHOOK_PORT", "8080"))


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Обработка POST запроса от GitHub"""
        if self.path != "/webhook":
            self.send_response(404)
            self.end_headers()
            return

        # Получаем заголовки
        signature = self.headers.get("X-Hub-Signature-256", "")
        content_type = self.headers.get("Content-Type", "")

        # Читаем тело запроса
        content_length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(content_length)

        # Проверяем подпись (безопасность)
        if WEBHOOK_SECRET and WEBHOOK_SECRET != "your_secret_key_here":
            expected_signature = (
                "sha256="
                + hmac.new(
                    WEBHOOK_SECRET.encode(), payload, hashlib.sha256
                ).hexdigest()
            )
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("❌ Неверная подпись webhook!")
                self.send_response(401)
                self.end_headers()
                return

        # Парсим JSON
        try:
            if content_type == "application/json":
                event = json.loads(payload.decode())
            else:
                event = {}
        except Exception as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            self.send_response(400)
            self.end_headers()
            return

        # Проверяем, что это push событие
        event_type = self.headers.get("X-GitHub-Event", "")
        if event_type == "push":
            logger.info("🔄 Получен push от GitHub, запускаем обновление...")
            try:
                # Запускаем скрипт обновления
                result = subprocess.run(
                    ["/bin/bash", f"{PROJECT_DIR}/update.sh"],
                    cwd=PROJECT_DIR,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode == 0:
                    logger.info("✅ Обновление завершено успешно!")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"status": "success", "message": "Обновление завершено"}).encode()
                    )
                else:
                    logger.error(f"❌ Ошибка при обновлении: {result.stderr}")
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"status": "error", "message": result.stderr}).encode()
                    )
            except subprocess.TimeoutExpired:
                logger.error("❌ Таймаут при обновлении")
                self.send_response(500)
                self.end_headers()
            except Exception as e:
                logger.error(f"❌ Ошибка: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            logger.info(f"ℹ️  Игнорируем событие: {event_type}")
            self.send_response(200)
            self.end_headers()

    def do_GET(self):
        """Проверка работоспособности"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Переопределяем логирование"""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Запуск webhook сервера"""
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, WebhookHandler)
    logger.info(f"🚀 Webhook сервер запущен на порту {PORT}")
    logger.info(f"📁 Директория проекта: {PROJECT_DIR}")
    logger.info(f"🔗 URL для GitHub webhook: http://your_server_ip:{PORT}/webhook")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("⏹️  Остановка webhook сервера...")
        httpd.shutdown()


if __name__ == "__main__":
    main()

