import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import ClientError

from config import BOT_TOKEN, get_random_proxy, load_proxies
from handlers import router
from profile_handlers import router as profile_router
from setup_bot import setup_bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_bot_with_proxy(use_proxy: bool = True) -> Bot:
    """Создание бота с прокси (или без, если флаг отключен)"""
    if not use_proxy:
        logger.info("Прокси отключены. Используем прямое подключение к Telegram.")
        return Bot(token=BOT_TOKEN)

    proxies = load_proxies()

    if not proxies:
        logger.warning("Прокси не найдены. Бот будет работать без прокси.")
        return Bot(token=BOT_TOKEN)

    # Выбираем случайный прокси
    proxy_url = get_random_proxy()
    if proxy_url:
        logger.info(f"Используется прокси: {proxy_url[:50]}...")
    else:
        logger.warning("Не удалось получить прокси. Бот будет работать без прокси.")
        return Bot(token=BOT_TOKEN)

    # Создаем кастомную сессию для aiogram с прокси
    # Прокси уже содержит авторизацию в формате http://user:pass@host:port
    try:
        aiohttp_session = AiohttpSession(proxy=proxy_url)
        return Bot(token=BOT_TOKEN, session=aiohttp_session)
    except RuntimeError as e:
        if "aiohttp-socks" in str(e).lower() or "aiohttp_socks" in str(e).lower():
            logger.error(
                "Модуль aiohttp-socks не установлен. "
                "Установите его командой: pip install aiohttp-socks python-socks[asyncio]"
            )
            logger.warning("Бот будет работать без прокси.")
            return Bot(token=BOT_TOKEN)
        else:
            raise
    except Exception as e:
        logger.error(f"Ошибка при создании сессии с прокси: {e}")
        logger.warning("Бот будет работать без прокси.")
        return Bot(token=BOT_TOKEN)


def create_dispatcher() -> Dispatcher:
    """Создание нового диспетчера с зарегистрированными роутерами"""
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)
    dispatcher.include_router(profile_router)
    return dispatcher


async def run_bot(use_proxy: bool = True):
    """Единичный цикл жизни бота"""
    bot = create_bot_with_proxy(use_proxy=use_proxy)
    dp = create_dispatcher()

    # Автоматическая настройка бота
    logger.info("Настройка бота...")
    await setup_bot(bot)

    logger.info("Запуск бота...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен и готов к работе!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


async def main():
    """Главная функция с автоматическим перезапуском при сбоях"""
    restart_delay = 5
    attempt = 1
    use_proxy = True
    proxy_failures = 0

    while True:
        try:
            await run_bot(use_proxy=use_proxy)
        except asyncio.CancelledError:
            raise
        except ClientError:
            logger.exception(
                "Сбой сети/прокси при работе бота (попытка %s). Перезапуск через %s c.",
                attempt,
                restart_delay,
            )
            if use_proxy:
                proxy_failures += 1
                if proxy_failures >= 3:
                    use_proxy = False
                    proxy_failures = 0
                    logger.warning(
                        "Прокси трижды подряд упали. Работаем дальше без прокси."
                    )
            await asyncio.sleep(restart_delay)
            attempt += 1
            restart_delay = min(restart_delay * 2, 300)
        except Exception:
            proxy_failures = 0
            logger.exception(
                "Критическая ошибка при работе бота (попытка %s). Перезапуск через %s c.",
                attempt,
                restart_delay,
            )
            await asyncio.sleep(restart_delay)
            attempt += 1
            restart_delay = min(restart_delay * 2, 300)
        else:
            break


if __name__ == "__main__":
    asyncio.run(main())
