from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import AREA_OPTIONS, LOCATIONS, find_nearest_locations


def get_storage_type_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа хранения"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Личные вещи"))
    builder.add(KeyboardButton(text="Мебель, бытовая техника"))
    builder.add(KeyboardButton(text="Товары для бизнеса"))
    builder.add(KeyboardButton(text="Оборудование"))
    builder.add(KeyboardButton(text="Архив"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_area_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора площади"""
    builder = ReplyKeyboardBuilder()
    for key, value in AREA_OPTIONS.items():
        builder.add(KeyboardButton(text=f"{value['name']} - {value['price_from']}"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_location_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора локации"""
    builder = InlineKeyboardBuilder()
    for location in LOCATIONS:
        name = location["name"]
        if location["is_promotion"]:
            name = f"🔥 АКЦИЯ! {name}"
        schedule = location["schedule"]
        if location["has_forklift"]:
            name += " (есть вилочный погрузчик)"
        # Ограничиваем длину текста для кнопки
        button_text = f"{name} ({schedule})"
        if len(button_text) > 64:  # Максимальная длина текста кнопки
            button_text = button_text[:61] + "..."
        builder.add(
            InlineKeyboardButton(
                text=button_text, callback_data=f"location_{location['id']}"
            )
        )
    builder.adjust(1)
    return builder.as_markup()


def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура Да/Нет"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Да"))
    builder.add(KeyboardButton(text="Нет"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_meeting_type_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа встречи"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Выбрать дату и время встречи"))
    builder.add(KeyboardButton(text="Заказать обратный звонок"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отменить"))
    return builder.as_markup(resize_keyboard=True)


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой поделиться контактом"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📱 Поделиться контактом", request_contact=True))
    builder.add(KeyboardButton(text="✏️ Ввести вручную"))
    builder.add(KeyboardButton(text="❌ Отменить"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_location_request_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой поделиться геолокацией"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📍 Поделиться геолокацией", request_location=True))
    builder.add(KeyboardButton(text="📋 Выбрать из списка"))
    builder.add(KeyboardButton(text="❌ Отменить"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_nearest_locations_keyboard(
    user_lat: float, user_lon: float, limit: int = 5
) -> InlineKeyboardMarkup:
    """Клавиатура с ближайшими локациями"""
    builder = InlineKeyboardBuilder()
    nearest = find_nearest_locations(user_lat, user_lon, limit)

    for location in nearest:
        name = location["name"]
        if location["is_promotion"]:
            name = f"🔥 {name}"
        if location["has_forklift"]:
            name += " 🚜"

        distance = location["distance"]
        if distance < 1:
            distance_text = f"{distance * 1000:.0f} м"
        else:
            distance_text = f"{distance:.1f} км"

        button_text = f"📍 {name} ({distance_text})"
        if len(button_text) > 64:
            button_text = button_text[:61] + "..."

        builder.add(
            InlineKeyboardButton(
                text=button_text, callback_data=f"location_{location['id']}"
            )
        )

    # Добавляем кнопку "Показать все локации"
    builder.add(
        InlineKeyboardButton(
            text="📋 Показать все локации", callback_data="show_all_locations"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def get_applications_keyboard(applications: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком заявок"""
    from datetime import datetime

    builder = InlineKeyboardBuilder()

    for app in applications[:10]:  # Показываем максимум 10 заявок
        app_id = app["id"]
        created_at = app["created_at"]

        # Парсим дату
        if isinstance(created_at, str):
            try:
                if "T" in created_at:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%d.%m.%Y")
            except:
                date_str = created_at[:10] if len(created_at) > 10 else created_at
        else:
            date_str = (
                str(created_at)[:10] if len(str(created_at)) > 10 else str(created_at)
            )

        status_emoji = {
            "completed": "✅",
            "processing": "🔄",
            "cancelled": "❌",
            "pending": "⏳",
        }.get(app.get("status", "pending"), "⏳")

        button_text = f"{status_emoji} Заявка #{app_id} ({date_str})"
        if len(button_text) > 64:
            button_text = button_text[:61] + "..."

        builder.add(
            InlineKeyboardButton(text=button_text, callback_data=f"view_app_{app_id}")
        )

    builder.adjust(1)
    return builder.as_markup()


def get_application_actions_keyboard(application_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с действиями для заявки"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="❌ Удалить заявку", callback_data=f"delete_app_{application_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="◀️ Назад к списку", callback_data="back_to_applications"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура профиля"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📋 Мои заявки", callback_data="my_applications")
    )
    builder.adjust(1)
    return builder.as_markup()
