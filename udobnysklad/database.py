"""
Модуль для работы с базой данных SQLite
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("bot_database.db")


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Инициализация базы данных"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Таблица заявок
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        username TEXT,
                        phone TEXT NOT NULL,
                        storage_type TEXT NOT NULL,
                        area TEXT NOT NULL,
                        location_id TEXT NOT NULL,
                        loaders TEXT,
                        meeting_type TEXT NOT NULL,
                        date_time TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        admin_message_id INTEGER,
                        status TEXT DEFAULT 'pending'
                    )
                """
                )

                # Таблица пользователей (для статистики)
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.commit()
                logger.info("База данных инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка при инициализации БД: {e}")

    def add_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ):
        """Добавить или обновить пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_activity)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (user_id, username, first_name, last_name),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")

    def create_application(
        self,
        user_id: int,
        application_data: Dict,
        admin_message_id: Optional[int] = None,
    ) -> int:
        """Создать новую заявку"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO applications (
                        user_id, username, phone, storage_type, area, location_id,
                        loaders, meeting_type, date_time, admin_message_id, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                    (
                        user_id,
                        application_data.get("username"),
                        application_data.get("phone"),
                        application_data.get("storage_type"),
                        application_data.get("area"),
                        application_data.get("location_id"),
                        application_data.get("loaders"),
                        application_data.get("meeting_type"),
                        application_data.get("date_time"),
                        admin_message_id,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Ошибка при создании заявки: {e}")
            return None

    def get_user_applications(self, user_id: int) -> List[Dict]:
        """Получить все заявки пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM applications
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                """,
                    (user_id,),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении заявок: {e}")
            return []

    def get_application(self, application_id: int, user_id: int) -> Optional[Dict]:
        """Получить заявку по ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM applications
                    WHERE id = ? AND user_id = ?
                """,
                    (application_id, user_id),
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении заявки: {e}")
            return None

    def update_application(
        self, application_id: int, user_id: int, updates: Dict
    ) -> bool:
        """Обновить заявку"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                set_clause += ", updated_at = CURRENT_TIMESTAMP"
                values = list(updates.values()) + [application_id, user_id]

                cursor.execute(
                    f"""
                    UPDATE applications
                    SET {set_clause}
                    WHERE id = ? AND user_id = ?
                """,
                    values,
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при обновлении заявки: {e}")
            return False

    def delete_application(self, application_id: int, user_id: int) -> Optional[Dict]:
        """Удалить заявку и вернуть данные для удаления из админ-чата"""
        try:
            # Сначала получаем данные заявки
            application = self.get_application(application_id, user_id)
            if not application:
                return None

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    DELETE FROM applications
                    WHERE id = ? AND user_id = ?
                """,
                    (application_id, user_id),
                )
                conn.commit()
                return application
        except Exception as e:
            logger.error(f"Ошибка при удалении заявки: {e}")
            return None

    def get_user_stats(self, user_id: int) -> Dict:
        """Получить статистику пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Общее количество заявок
                cursor.execute(
                    """
                    SELECT COUNT(*) as total FROM applications WHERE user_id = ?
                """,
                    (user_id,),
                )
                total = cursor.fetchone()["total"]

                # Заявки по статусам
                cursor.execute(
                    """
                    SELECT status, COUNT(*) as count
                    FROM applications
                    WHERE user_id = ?
                    GROUP BY status
                """,
                    (user_id,),
                )
                statuses = {row["status"]: row["count"] for row in cursor.fetchall()}

                # Последняя заявка
                cursor.execute(
                    """
                    SELECT * FROM applications
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """,
                    (user_id,),
                )
                last_application = cursor.fetchone()

                return {
                    "total": total,
                    "statuses": statuses,
                    "last_application": (
                        dict(last_application) if last_application else None
                    ),
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return {"total": 0, "statuses": {}, "last_application": None}


# Глобальный экземпляр БД
db = Database()
