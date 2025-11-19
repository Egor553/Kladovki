"""
Модуль для автоматической настройки бота
"""

import logging
from pathlib import Path
from aiogram import Bot
from aiogram.types import BotCommand, FSInputFile
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


async def setup_bot(bot: Bot, force: bool = False):
    """
    Автоматическая настройка бота: название, описание, фото, команды

    Args:
        bot: Экземпляр бота
        force: Принудительная настройка (по умолчанию False - пропускает при flood control)
    """
    try:
        # Название бота
        try:
            await bot.set_my_name("Удобный Склад")
            logger.info("✅ Название бота установлено: Удобный Склад")
        except TelegramBadRequest as e:
            if (
                "flood control" in str(e).lower()
                or "too many requests" in str(e).lower()
            ):
                logger.warning(
                    "⚠️ Flood control: название бота уже установлено или слишком частые запросы. Пропускаем."
                )
            else:
                raise

        # Описание бота
        try:
            description = (
                "🏢 Бот для аренды складских помещений в Челябинской области\n\n"
                "📍 15 локаций по всему городу\n"
                "💰 От 1000₽/месяц\n"
                "🔒 Охраняемые площадки с видеонаблюдением\n"
                "⏰ Круглосуточный доступ\n\n"
                "Оформите заявку на аренду склада прямо сейчас!"
            )
            await bot.set_my_description(description)
            logger.info("✅ Описание бота установлено")
        except TelegramBadRequest as e:
            if (
                "flood control" in str(e).lower()
                or "too many requests" in str(e).lower()
            ):
                logger.warning(
                    "⚠️ Flood control: описание бота уже установлено. Пропускаем."
                )
            else:
                raise

        # Короткое описание (для чатов)
        try:
            short_description = "🏢 Аренда складских помещений в Челябинске. От 1000₽/месяц. 15 локаций. Охраняемые площадки."
            await bot.set_my_short_description(short_description)
            logger.info("✅ Короткое описание бота установлено")
        except TelegramBadRequest as e:
            if (
                "flood control" in str(e).lower()
                or "too many requests" in str(e).lower()
            ):
                logger.warning(
                    "⚠️ Flood control: короткое описание бота уже установлено. Пропускаем."
                )
            else:
                raise

        # Команды бота
        try:
            commands = [
                BotCommand(
                    command="start",
                    description="🚀 Начать оформление заявки на аренду склада",
                ),
                BotCommand(command="cancel", description="❌ Отменить текущую заявку"),
                BotCommand(command="profile", description="👤 Мой профиль и заявки"),
            ]
            await bot.set_my_commands(commands)
            logger.info("✅ Команды бота установлены")
        except TelegramBadRequest as e:
            if (
                "flood control" in str(e).lower()
                or "too many requests" in str(e).lower()
            ):
                logger.warning(
                    "⚠️ Flood control: команды бота уже установлены. Пропускаем."
                )
            else:
                raise

        # Установка фото бота
        # Примечание: В некоторых версиях aiogram метод set_my_photo может быть недоступен
        # Фото можно установить вручную через @BotFather в Telegram
        photo_path = Path("загруженное (9).png")
        if not photo_path.exists():
            # Пробуем другие возможные имена
            possible_names = [
                "загруженное (9).png",
                "logo.png",
                "bot_photo.png",
                "avatar.png",
            ]
            photo_path = None
            for name in possible_names:
                path = Path(name)
                if path.exists():
                    photo_path = path
                    break

        if photo_path and photo_path.exists():
            # Установка фото бота
            # Примечание: В текущей версии aiogram 3.x метод set_my_photo может быть недоступен
            # Фото нужно установить вручную через @BotFather
            logger.info(
                f"📸 Файл с фото найден: {photo_path}\n"
                "ℹ️ Для установки фото бота выполните следующие шаги:\n"
                "1. Откройте @BotFather в Telegram\n"
                "2. Отправьте команду /setuserpic\n"
                "3. Выберите вашего бота (@Udobnysklad_bot)\n"
                "4. Отправьте файл 'загруженное (9).png'\n\n"
                "✅ Остальные настройки бота применены успешно!"
            )
        else:
            logger.warning("⚠️ Файл с фото бота не найден. Пропускаем установку фото.")

        logger.info("✅ Автоматическая настройка бота завершена успешно!")

    except TelegramBadRequest as e:
        if "flood control" in str(e).lower() or "too many requests" in str(e).lower():
            logger.warning(
                "⚠️ Flood control: настройки бота уже установлены или слишком частые запросы. "
                "Бот продолжит работу с текущими настройками."
            )
        else:
            logger.error(f"❌ Ошибка при настройке бота: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка при настройке бота: {e}")
