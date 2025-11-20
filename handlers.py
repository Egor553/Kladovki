import logging
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import (ADMIN_CHAT_ID, AREA_OPTIONS, LOADERS_CONTACT, LOCATIONS,
                    find_nearest_locations, get_map_link)
from database import db
from keyboards import (get_application_actions_keyboard,
                       get_applications_keyboard, get_area_keyboard,
                       get_cancel_keyboard, get_location_keyboard,
                       get_location_request_keyboard,
                       get_meeting_type_keyboard,
                       get_nearest_locations_keyboard, get_phone_keyboard,
                       get_profile_keyboard, get_storage_type_keyboard,
                       get_yes_no_keyboard)

logger = logging.getLogger(__name__)

CHELYABINSK_TZ = ZoneInfo("Asia/Yekaterinburg")

router = Router()


class OrderStates(StatesGroup):
    waiting_for_storage_type = State()
    waiting_for_area = State()
    waiting_for_location = State()
    waiting_for_loaders = State()
    waiting_for_meeting_type = State()
    waiting_for_date_time = State()
    waiting_for_phone = State()


def format_application(data: dict) -> str:
    """Форматирование заявки для отправки в админ-чат"""
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

    chelyabinsk_now = datetime.now(CHELYABINSK_TZ)
    text += (
        f"\n🕐 <b>Время заявки (Челябинск):</b> "
        f"{chelyabinsk_now.strftime('%d.%m.%Y %H:%M')}"
    )

    return text


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()

    # Сохраняем/обновляем пользователя в БД
    db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    await message.answer(
        "👋 <b>Добро пожаловать в Удобный Склад!</b>\n\n"
        "🏢 Мы предлагаем аренду складских помещений в Челябинской области\n\n"
        "✨ <b>Наши преимущества:</b>\n"
        "📍 15 удобных локаций по всему городу\n"
        "💰 От 1000₽/месяц\n"
        "🔒 Охраняемые площадки с видеонаблюдением\n"
        "⏰ Круглосуточный доступ\n"
        "🚚 Услуги газели и грузчиков\n\n"
        "Я помогу вам оформить заявку на аренду склада. Начнем?",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await message.answer(
        "1️⃣ <b>Что вы собираетесь хранить?</b>\n\n" "Выберите один из вариантов:",
        reply_markup=get_storage_type_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(OrderStates.waiting_for_storage_type)


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отменить")
async def cmd_cancel(message: Message, state: FSMContext):
    """Обработчик отмены"""
    await state.clear()
    await message.answer(
        "❌ Заявка отменена.\n\n" "Для начала новой заявки используйте /start",
        reply_markup=None,
    )


@router.message(StateFilter(OrderStates.waiting_for_storage_type))
async def process_storage_type(message: Message, state: FSMContext):
    """Обработка типа хранения"""
    storage_types = [
        "Личные вещи",
        "Мебель, бытовая техника",
        "Товары для бизнеса",
        "Оборудование",
        "Архив",
    ]

    if message.text not in storage_types:
        await message.answer("❌ Пожалуйста, выберите вариант из предложенных:")
        return

    await state.update_data(
        storage_type=message.text, username=message.from_user.username or "не указан"
    )

    await message.answer(
        "✅ Отлично!\n\n" "2️⃣ <b>Выберите площадь:</b>",
        reply_markup=get_area_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(OrderStates.waiting_for_area)


@router.message(StateFilter(OrderStates.waiting_for_area))
async def process_area(message: Message, state: FSMContext):
    """Обработка площади"""
    # Ищем выбранную площадь в тексте
    selected_area = None
    for key, value in AREA_OPTIONS.items():
        if value["name"] in message.text:
            selected_area = key
            break

    if not selected_area:
        await message.answer("❌ Пожалуйста, выберите вариант из предложенных:")
        return

    area_info = AREA_OPTIONS[selected_area]
    await state.update_data(area=selected_area)

    await message.answer(
        f"✅ Выбрано: {area_info['name']}\n"
        f"Размеры: {area_info['dimensions']}\n"
        f"Цена: {area_info['price_from']}\n\n"
        "3️⃣ <b>Выберите локацию:</b>\n\n"
        "Примечание: стоимость боксов зависит от локации площадки.\n\n"
        "Вы можете поделиться своей геолокацией для поиска ближайшего склада или выбрать из списка.",
        reply_markup=get_location_request_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(OrderStates.waiting_for_location)


@router.callback_query(
    StateFilter(OrderStates.waiting_for_location), F.data.startswith("location_")
)
async def process_location(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора локации"""
    location_id = callback.data.split("_")[1]
    location = next((loc for loc in LOCATIONS if loc["id"] == location_id), None)

    if not location:
        await callback.answer("Ошибка выбора локации", show_alert=True)
        return

    await state.update_data(location_id=location_id)

    location_text = location["name"]
    if location["is_promotion"]:
        location_text = f"🔥 АКЦИЯ! {location_text}"
    if location["has_forklift"]:
        location_text += " (есть вилочный погрузчик)"

    # Добавляем ссылку на карту
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    map_link = get_map_link(location.get("address", location["name"]))

    await callback.message.edit_text(
        f"✅ Выбрана локация: {location_text}\n"
        f"График работы: {location['schedule']}"
    )

    # Отправляем отдельное сообщение с кнопкой карты и следующим вопросом
    map_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📍 Открыть на карте", url=map_link)]
        ]
    )

    await callback.message.answer(
        "📍 <b>Адрес:</b> " + location.get("address", location["name"]) + "\n\n"
        "4️⃣ <b>Нужна ли газель и грузчики?</b>\n\n"
        "Выберите вариант:",
        parse_mode="HTML",
        reply_markup=get_yes_no_keyboard(),
    )

    # Отправляем кнопку с картой отдельным сообщением
    await callback.message.answer("📍 Построить маршрут:", reply_markup=map_keyboard)
    await state.set_state(OrderStates.waiting_for_loaders)
    await callback.answer()


@router.message(StateFilter(OrderStates.waiting_for_loaders))
async def process_loaders(message: Message, state: FSMContext):
    """Обработка вопроса о газели и грузчиках"""
    if message.text not in ["Да", "Нет"]:
        await message.answer("❌ Пожалуйста, выберите 'Да' или 'Нет':")
        return

    await state.update_data(loaders=message.text)

    if message.text == "Да":
        await message.answer(
            f"✅ Понятно, вам нужна газель и грузчики.\n"
            f"📞 Контакт: {LOADERS_CONTACT}\n\n"
            "5️⃣ <b>Выберите тип встречи:</b>",
            reply_markup=get_meeting_type_keyboard(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "✅ Понятно.\n\n" "5️⃣ <b>Выберите тип встречи:</b>",
            reply_markup=get_meeting_type_keyboard(),
            parse_mode="HTML",
        )
    await state.set_state(OrderStates.waiting_for_meeting_type)


@router.message(StateFilter(OrderStates.waiting_for_meeting_type))
async def process_meeting_type(message: Message, state: FSMContext):
    """Обработка типа встречи"""
    if message.text == "Выбрать дату и время встречи":
        await state.update_data(meeting_type=message.text)
        await message.answer(
            "📅 <b>Введите дату и время встречи:</b>\n\n"
            "Формат: ДД.ММ.ГГГГ ЧЧ:ММ\n"
            "Например: 25.12.2024 14:30\n\n"
            "Рабочее время: с 9:00 до 22:00",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(OrderStates.waiting_for_date_time)
    elif message.text == "Заказать обратный звонок":
        await state.update_data(meeting_type=message.text)
        await message.answer(
            "📞 <b>Введите ваш номер телефона:</b>\n\n"
            "Вы можете поделиться контактом или ввести номер вручную.",
            reply_markup=get_phone_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(OrderStates.waiting_for_phone)
    else:
        await message.answer("❌ Пожалуйста, выберите вариант из предложенных:")


@router.message(StateFilter(OrderStates.waiting_for_date_time))
async def process_date_time(message: Message, state: FSMContext):
    """Обработка даты и времени встречи"""
    # Простая валидация формата, допускаем лишние пробелы и однозначные числа
    user_input = message.text.strip()
    pattern = r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})\s*$"
    match = re.match(pattern, user_input)

    if not match:
        await message.answer(
            "❌ Неверный формат. Используйте формат: ДД.ММ.ГГГГ ЧЧ:ММ\n"
            "Например: 25.12.2024 14:30"
        )
        return

    day, month, year, hour, minute = map(int, match.groups())

    # Проверка времени (9:00 - 22:00)
    if hour < 9 or hour > 22:
        await message.answer(
            "❌ Время должно быть в рабочем диапазоне: с 9:00 до 22:00"
        )
        return

    try:
        # Проверка корректности даты
        selected_datetime = datetime(
            year, month, day, hour, minute, tzinfo=CHELYABINSK_TZ
        )
        # Проверка, что дата не в прошлом
        # Округляем текущее время до минут для корректного сравнения
        now = datetime.now(CHELYABINSK_TZ).replace(second=0, microsecond=0)
        if selected_datetime < now:
            await message.answer(
                "❌ Нельзя выбрать дату в прошлом. Пожалуйста, выберите будущую дату."
            )
            return
    except ValueError:
        await message.answer("❌ Неверная дата. Проверьте правильность ввода.")
        return

    await state.update_data(date_time=selected_datetime.strftime("%d.%m.%Y %H:%M"))
    await message.answer(
        "📞 <b>Введите ваш номер телефона:</b>\n\n"
        "Вы можете поделиться контактом или ввести номер вручную.",
        reply_markup=get_phone_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(OrderStates.waiting_for_phone)


@router.message(StateFilter(OrderStates.waiting_for_location), F.location)
async def process_location_geo(message: Message, state: FSMContext):
    """Обработка геолокации для поиска ближайшего склада"""
    user_location = message.location
    user_lat = user_location.latitude
    user_lon = user_location.longitude

    # Находим ближайшие локации
    nearest = find_nearest_locations(user_lat, user_lon, limit=5)

    if nearest:
        # Формируем сообщение с ближайшими локациями
        text = "📍 <b>Найдены ближайшие склады к вашему местоположению:</b>\n\n"

        for i, location in enumerate(nearest[:3], 1):  # Показываем топ-3
            distance = location["distance"]
            if distance < 1:
                distance_text = f"{distance * 1000:.0f} м"
            else:
                distance_text = f"{distance:.1f} км"

            name = location["name"]
            if location["is_promotion"]:
                name = f"🔥 {name}"

            text += f"{i}. {name} - <b>{distance_text}</b>\n"
            text += f"   {location['schedule']}\n\n"

        await message.answer(
            text + "Выберите ближайшую локацию:",
            reply_markup=get_nearest_locations_keyboard(user_lat, user_lon),
            parse_mode="HTML",
        )
    else:
        # Если не найдены локации с координатами, показываем все
        await message.answer(
            "📍 <b>Спасибо за геолокацию!</b>\n\n"
            "Выберите удобную для вас локацию из списка:",
            reply_markup=get_location_keyboard(),
            parse_mode="HTML",
        )


@router.message(
    StateFilter(OrderStates.waiting_for_location), F.text == "📋 Выбрать из списка"
)
async def process_location_list(message: Message, state: FSMContext):
    """Обработка выбора локации из списка"""
    await message.answer(
        "📍 <b>Выберите локацию из списка:</b>",
        reply_markup=get_location_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(
    StateFilter(OrderStates.waiting_for_location), F.data == "show_all_locations"
)
async def show_all_locations_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки 'Показать все локации'"""
    await callback.message.edit_text(
        "📍 <b>Все доступные локации:</b>",
        reply_markup=get_location_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(StateFilter(OrderStates.waiting_for_phone), F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    """Обработка контакта из Telegram"""
    contact = message.contact
    phone = contact.phone_number

    # Нормализация номера
    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    elif not phone.startswith("+"):
        phone = "+" + phone

    await state.update_data(phone=phone)
    await finish_application(message, state)


@router.message(
    StateFilter(OrderStates.waiting_for_phone), F.text == "✏️ Ввести вручную"
)
async def process_phone_manual(message: Message, state: FSMContext):
    """Обработка выбора ручного ввода телефона"""
    await message.answer(
        "📞 <b>Введите номер телефона вручную:</b>\n\n"
        "Формат: +7XXXXXXXXXX или 8XXXXXXXXXX\n"
        "Например: +79991234567 или 89991234567",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(StateFilter(OrderStates.waiting_for_phone), F.text)
async def process_phone(message: Message, state: FSMContext):
    """Обработка номера телефона и завершение заявки"""
    # Пропускаем служебные кнопки
    if message.text in ["✏️ Ввести вручную", "❌ Отменить"]:
        return

    # Валидация номера телефона
    phone_pattern = r"^(\+7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$"
    phone_clean = re.sub(r"[\s\-\(\)]", "", message.text)

    if not re.match(r"^(\+7|8)?\d{10}$", phone_clean):
        await message.answer(
            "❌ Неверный формат номера. Используйте формат:\n"
            "+79991234567 или 89991234567"
        )
        return

    # Нормализация номера
    if phone_clean.startswith("8"):
        phone_clean = "+7" + phone_clean[1:]
    elif not phone_clean.startswith("+7"):
        phone_clean = "+7" + phone_clean

    await state.update_data(phone=phone_clean)
    await finish_application(message, state)


async def finish_application(message: Message, state: FSMContext):
    """Завершение заявки и отправка в админ-чат"""
    data = await state.get_data()

    # Добавляем user_id в данные
    data["user_id"] = message.from_user.id
    data["username"] = message.from_user.username or "не указан"

    # Формирование и отправка заявки
    application_text = format_application(data)

    # Отправка заявки в админ-чат и сохранение message_id
    admin_message_id = None
    if ADMIN_CHAT_ID:
        try:
            sent_message = await message.bot.send_message(
                ADMIN_CHAT_ID, application_text, parse_mode="HTML"
            )
            admin_message_id = sent_message.message_id
        except Exception as e:
            logger.error(f"Ошибка отправки в админ-чат: {e}")
            logger.error(f"Заявка не отправлена в админ-чат: {application_text}")

    # Сохранение заявки в БД
    application_id = db.create_application(
        user_id=message.from_user.id,
        application_data=data,
        admin_message_id=admin_message_id,
    )

    # Отправка пользователю подтверждение
    await message.answer(
        "✅ <b>Заявка успешно оформлена!</b>\n\n"
        f"📋 <b>Номер заявки:</b> #{application_id}\n\n"
        "Наш менеджер свяжется с вами в ближайшее время.\n\n"
        "Для оформления новой заявки используйте /start\n"
        "Для просмотра ваших заявок используйте /profile",
        reply_markup=None,
        parse_mode="HTML",
    )

    await state.clear()
