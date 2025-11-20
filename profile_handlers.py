"""
Обработчики для профиля пользователя
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime
from keyboards import (
    get_applications_keyboard,
    get_application_actions_keyboard,
    get_profile_keyboard,
)
from config import AREA_OPTIONS, LOCATIONS, ADMIN_CHAT_ID, CHELYABINSK_TZ, LOADERS_CONTACT, get_map_link
from database import db
import logging

# Импортируем функции форматирования из handlers
def format_application_for_admin(data: dict) -> str:
    """Форматирование заявки для отправки в админ-чат (копия из handlers)"""
    location = next(
        (loc for loc in LOCATIONS if loc["id"] == data.get("location_id")), None
    )
    location_name = location["name"] if location else "Не указано"
    location_address = (
        location.get("address", location_name) if location else "Не указано"
    )

    area_info = AREA_OPTIONS.get(data.get("area", ""), {})
    area_name = area_info.get("name", "Не указано")

    text = f"""
📋 <b>НОВАЯ ЗАЯВКА</b>

👤 <b>Пользователь:</b> @{data.get('username', 'не указан')}
🆔 <b>ID пользователя:</b> {data.get('user_id', 'не указан')}
📞 <b>Телефон:</b> {data.get('phone', 'не указан')}

1️⃣ <b>Тип хранения:</b> {data.get('storage_type', 'не указано')}

2️⃣ <b>Площадь:</b> {area_name}
   {area_info.get('dimensions', '')}
   {area_info.get('price_from', '')}

3️⃣ <b>Локация:</b> {location_name}
   Адрес: {location_address}
   График работы: {location['schedule'] if location else 'не указано'}
   {'✅ Есть вилочный погрузчик' if location and location.get('has_forklift') else ''}
   {'🔥 АКЦИЯ' if location and location.get('is_promotion') else ''}
   {'📍 ' + get_map_link(location_address) if location else ''}

4️⃣ <b>Газель и грузчики:</b> {data.get('loaders', 'не указано')}
   {f'📞 Контакт: {LOADERS_CONTACT}' if data.get('loaders') == 'Да' else ''}

5️⃣ <b>Тип встречи:</b> {data.get('meeting_type', 'не указано')}
"""

    if data.get("meeting_type") == "Выбрать дату и время встречи":
        text += f"   📅 Дата и время: {data.get('date_time', 'не указано')}\n"
    elif data.get("meeting_type") == "Заказать обратный звонок":
        text += "   📞 Обратный звонок запрошен\n"

    created_at_display = None
    created_at_raw = data.get("created_at")

    if isinstance(created_at_raw, datetime):
        created_at_display = created_at_raw.astimezone(CHELYABINSK_TZ).strftime(
            "%d.%m.%Y %H:%M"
        )
    elif isinstance(created_at_raw, str):
        try:
            parsed_dt = datetime.fromisoformat(created_at_raw)
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=CHELYABINSK_TZ)
            created_at_display = parsed_dt.astimezone(CHELYABINSK_TZ).strftime(
                "%d.%m.%Y %H:%M"
            )
        except ValueError:
            pass

    if not created_at_display:
        created_at_display = datetime.now(CHELYABINSK_TZ).strftime("%d.%m.%Y %H:%M")

    text += f"\n🕐 <b>Время заявки (Челябинск):</b> {created_at_display}"

    return text


def format_application_cancelled(original_text: str, user_id: int, username: str) -> str:
    """Добавление информации об отмене заявки к существующему тексту"""
    cancelled_info = f"\n\n❌ <b>ЗАЯВКА ОТМЕНЕНА</b>\n👤 <b>Пользователь отменил заявку:</b> {format_username(username)}\n🆔 <b>ID пользователя:</b> {user_id}"
    return original_text + cancelled_info

logger = logging.getLogger(__name__)

router = Router()


def format_username(username: str | None) -> str:
    """Подготовка ника пользователя для сообщений"""
    if not username:
        return "не указан"
    return username if username.startswith("@") else f"@{username}"


def format_application_for_user(app: dict) -> str:
    """Форматирование заявки для отображения пользователю"""
    location = next(
        (loc for loc in LOCATIONS if loc["id"] == app.get("location_id")), None
    )
    location_name = location["name"] if location else "Не указано"

    area_info = AREA_OPTIONS.get(app.get("area", ""), {})
    area_name = area_info.get("name", "Не указано")

    # Парсим дату создания
    created_at = app.get("created_at")
    if isinstance(created_at, str) and created_at:
        try:
            created_at_clean = created_at.replace("Z", "+00:00")
            if "T" in created_at_clean:
                dt = datetime.fromisoformat(created_at_clean)
            else:
                dt = datetime.strptime(created_at_clean, "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=CHELYABINSK_TZ)
            date_str = dt.astimezone(CHELYABINSK_TZ).strftime("%d.%m.%Y %H:%M")
        except Exception:
            date_str = created_at[:16] if len(created_at) > 16 else created_at
    elif isinstance(created_at, datetime):
        date_str = created_at.astimezone(CHELYABINSK_TZ).strftime("%d.%m.%Y %H:%M")
    else:
        if created_at:
            created_at_str = str(created_at)
            date_str = (
                created_at_str[:16]
                if len(created_at_str) > 16
                else created_at_str
            )
        else:
            date_str = "не указано"

    status_text = {
        "pending": "⏳ Ожидает обработки",
        "processing": "🔄 В обработке",
        "completed": "✅ Завершена",
        "cancelled": "❌ Отменена",
    }.get(app.get("status", "pending"), "⏳ Ожидает обработки")

    text = f"""
📋 <b>Заявка #{app['id']}</b>
{status_text}

📅 <b>Создана:</b> {date_str}

1️⃣ <b>Тип хранения:</b> {app.get('storage_type', 'не указано')}

2️⃣ <b>Площадь:</b> {area_name}
   {area_info.get('price_from', '')}

3️⃣ <b>Локация:</b> {location_name}
   График: {location['schedule'] if location else 'не указано'}

4️⃣ <b>Газель и грузчики:</b> {app.get('loaders', 'не указано')}

5️⃣ <b>Тип встречи:</b> {app.get('meeting_type', 'не указано')}
"""

    if app.get("date_time"):
        text += f"   📅 Дата и время: {app['date_time']}\n"

    text += f"\n📞 <b>Телефон:</b> {app.get('phone', 'не указано')}"

    return text


@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    """Обработчик команды /profile"""
    await state.clear()

    user_id = message.from_user.id
    stats = db.get_user_stats(user_id)

    text = f"""
👤 <b>Ваш профиль</b>

📊 <b>Статистика:</b>
📋 Всего заявок: {stats['total']}
"""

    if stats["statuses"]:
        for status, count in stats["statuses"].items():
            status_emoji = {
                "pending": "⏳",
                "processing": "🔄",
                "completed": "✅",
                "cancelled": "❌",
            }.get(status, "📋")
            status_name = {
                "pending": "Ожидает",
                "processing": "В обработке",
                "completed": "Завершена",
                "cancelled": "Отменена",
            }.get(status, status)
            text += f"{status_emoji} {status_name}: {count}\n"

    if stats["last_application"]:
        last_app = stats["last_application"]
        created_at = last_app.get("created_at")
        if isinstance(created_at, str) and created_at:
            try:
                created_at_clean = created_at.replace("Z", "+00:00")
                if "T" in created_at_clean:
                    dt = datetime.fromisoformat(created_at_clean)
                else:
                    dt = datetime.strptime(created_at_clean, "%Y-%m-%d %H:%M:%S")
                    dt = dt.replace(tzinfo=CHELYABINSK_TZ)
                date_str = dt.astimezone(CHELYABINSK_TZ).strftime("%d.%m.%Y %H:%M")
            except Exception:
                date_str = created_at[:16] if len(created_at) > 16 else created_at
        elif isinstance(created_at, datetime):
            date_str = created_at.astimezone(CHELYABINSK_TZ).strftime("%d.%m.%Y %H:%M")
        elif created_at:
            created_at_str = str(created_at)
            date_str = (
                created_at_str[:16]
                if len(created_at_str) > 16
                else created_at_str
            )
        else:
            date_str = "не указано"
        text += f"\n📋 Последняя заявка: #{last_app['id']} ({date_str})"

    await message.answer(text, reply_markup=get_profile_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "my_applications")
async def show_applications(callback: CallbackQuery, state: FSMContext):
    """Показать список заявок пользователя"""
    user_id = callback.from_user.id
    applications = db.get_user_applications(user_id)

    if not applications:
        try:
            await callback.message.edit_text(
                "📋 <b>У вас пока нет заявок</b>\n\n"
                "Создайте первую заявку с помощью команды /start",
                reply_markup=get_profile_keyboard(),
                parse_mode="HTML",
            )
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                logger.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.answer()
        return

    try:
        await callback.message.edit_text(
            f"📋 <b>Ваши заявки ({len(applications)}):</b>\n\n"
            "Выберите заявку для просмотра:",
            reply_markup=get_applications_keyboard(applications),
            parse_mode="HTML",
        )
    except Exception as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"Ошибка при редактировании сообщения: {e}")

    await callback.answer()


@router.callback_query(F.data == "my_stats")
async def show_stats(callback: CallbackQuery, state: FSMContext):
    """Показать статистику пользователя"""
    user_id = callback.from_user.id
    stats = db.get_user_stats(user_id)

    text = f"""
📊 <b>Ваша статистика</b>

📋 <b>Всего заявок:</b> {stats['total']}
"""

    if stats["statuses"]:
        text += "\n<b>По статусам:</b>\n"
        for status, count in stats["statuses"].items():
            status_emoji = {
                "pending": "⏳ Ожидает",
                "processing": "🔄 В обработке",
                "completed": "✅ Завершена",
                "cancelled": "❌ Отменена",
            }.get(status, f"📋 {status}")
            text += f"{status_emoji}: {count}\n"
    else:
        text += "\nУ вас пока нет заявок"

    # Используем answer вместо edit_text, чтобы избежать ошибки "message is not modified"
    try:
        await callback.message.edit_text(
            text, reply_markup=get_profile_keyboard(), parse_mode="HTML"
        )
    except Exception as e:
        # Игнорируем ошибку "message is not modified"
        if "message is not modified" not in str(e).lower():
            logger.error(f"Ошибка при редактировании сообщения: {e}")

    await callback.answer()


@router.callback_query(F.data == "back_to_applications")
async def back_to_applications(callback: CallbackQuery, state: FSMContext):
    """Вернуться к списку заявок"""
    user_id = callback.from_user.id
    applications = db.get_user_applications(user_id)

    if not applications:
        try:
            await callback.message.edit_text(
                "📋 <b>У вас пока нет заявок</b>\n\n"
                "Создайте первую заявку с помощью команды /start",
                reply_markup=get_profile_keyboard(),
                parse_mode="HTML",
            )
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                logger.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.answer()
        return

    try:
        await callback.message.edit_text(
            f"📋 <b>Ваши заявки ({len(applications)}):</b>\n\n"
            "Выберите заявку для просмотра:",
            reply_markup=get_applications_keyboard(applications),
            parse_mode="HTML",
        )
    except Exception as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"Ошибка при редактировании сообщения: {e}")

    await callback.answer()


@router.callback_query(F.data.startswith("view_app_"))
async def view_application(callback: CallbackQuery, state: FSMContext):
    """Просмотр конкретной заявки"""
    application_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    application = db.get_application(application_id, user_id)

    if not application:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    text = format_application_for_user(application)

    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_application_actions_keyboard(application_id),
            parse_mode="HTML",
        )
    except Exception as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"Ошибка при редактировании сообщения: {e}")

    await callback.answer()


@router.callback_query(F.data.startswith("delete_app_"))
async def delete_application(callback: CallbackQuery, state: FSMContext):
    """Удаление заявки"""
    application_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    # Удаляем заявку из БД и получаем данные для удаления из админ-чата
    application = db.delete_application(application_id, user_id)

    if not application:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    # Редактируем сообщение в админ-чате, добавляя информацию об отмене
    message_updated = False
    if ADMIN_CHAT_ID and application.get("admin_message_id"):
        try:
            username = (
                callback.from_user.username or application.get("username") or "не указан"
            )
            user_id_for_cancel = callback.from_user.id
            
            # Формируем текст заявки заново из данных application
            application_data = dict(application)
            application_data['user_id'] = application.get('user_id', user_id_for_cancel)
            application_data['username'] = application.get('username', username)
            
            # Добавляем created_at если его нет
            if 'created_at' not in application_data or not application_data.get('created_at'):
                application_data['created_at'] = datetime.now(CHELYABINSK_TZ).isoformat()
            
            # Формируем оригинальный текст заявки
            original_text = format_application_for_admin(application_data)
            
            # Добавляем информацию об отмене
            updated_text = format_application_cancelled(original_text, user_id_for_cancel, username)
            
            # Редактируем сообщение
            await callback.bot.edit_message_text(
                chat_id=ADMIN_CHAT_ID,
                message_id=application["admin_message_id"],
                text=updated_text,
                parse_mode="HTML"
            )
            message_updated = True
            logger.info(f"Сообщение заявки #{application_id} успешно обновлено в админ-чате")
        except Exception as e:
            logger.error(f"Ошибка при редактировании сообщения в админ-чате: {e}", exc_info=True)
            # Если не удалось отредактировать, отправляем новое сообщение
            username = (
                callback.from_user.username or application.get("username") or "не указан"
            )
            notify_text = (
                f"❌ Заявка #{application_id} отменена пользователем {format_username(username)}\n"
                f"🆔 ID пользователя: {callback.from_user.id}"
            )
            try:
                await callback.bot.send_message(ADMIN_CHAT_ID, notify_text, parse_mode="HTML")
                logger.info(f"Отправлено новое сообщение об отмене заявки #{application_id}")
            except Exception as send_error:
                logger.error(f"Ошибка при отправке уведомления об отмене заявки: {send_error}")

    # Получаем обновленный список заявок
    applications = db.get_user_applications(user_id)

    if applications:
        # Если есть еще заявки, показываем список
        try:
            await callback.message.edit_text(
                f"✅ <b>Заявка #{application_id} удалена</b>\n\n"
                f"{'Сообщение в админ-чате обновлено с информацией об отмене.' if message_updated else ''}\n\n"
                f"📋 <b>Ваши заявки ({len(applications)}):</b>\n\n"
                "Выберите заявку для просмотра:",
                reply_markup=get_applications_keyboard(applications),
                parse_mode="HTML",
            )
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                logger.error(f"Ошибка при редактировании сообщения: {e}")
    else:
        # Если заявок больше нет, возвращаемся в профиль
        try:
            await callback.message.edit_text(
                f"✅ <b>Заявка #{application_id} удалена</b>\n\n"
                f"{'Сообщение в админ-чате обновлено с информацией об отмене.' if message_updated else ''}\n\n"
                "📋 У вас больше нет заявок.\n"
                "Создайте новую заявку с помощью команды /start",
                reply_markup=get_profile_keyboard(),
                parse_mode="HTML",
            )
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                logger.error(f"Ошибка при редактировании сообщения: {e}")

    await callback.answer("Заявка удалена")
