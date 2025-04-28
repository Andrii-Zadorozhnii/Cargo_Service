
# Константы
BOT_TOKEN = "7671224104:AAGO1E0ssPTXjko_Ji7n3w0l3S8B52EeWzQ"
DRIVERS_GROUP_ID = "@Cargo_Service_Driver"
SALT = "Zador-74622"


import asyncio
import hashlib
import re
import uuid
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramAPIError
from aiogram.filters import Command
import logging
from django.conf import settings
from django.utils import timezone

from django.db import close_old_connections
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

# Изменения для SQLite
import sqlite3
from sqlite3 import Error

from cargo_bot.models import User, Cargo, Company, Manager, Customer
ukraine_cities = [
    "Александрия",
    "Алчевск",
    "Алешки",
    "Бахмут",
    "Бердянск",
    "Белая Церковь",
    "Борисполь",
    "Бровары",
    "Винница",
    "Горловка",
    "Днепр",
    "Дружковка",
    "Евпатория",
    "Житомир",
    "Желтые Воды",
    "Запорожье",
    "Ивано-Франковск",
    "Ирпень",
    "Каменец-Подольский",
    "Каменское",
    "Керчь",
    "Киев",
    "Коломыя",
    "Константиновка",
    "Краматорск",
    "Кривой Рог",
    "Кропивницкий",
    "Лисичанск",
    "Лозовая",
    "Луцк",
    "Львов",
    "Мариуполь",
    "Мелитополь",
    "Мукачево",
    "Николаев",
    "Никополь",
    "Новомосковск",
    "Нетишин",
    "Обухов",
    "Одесса",
    "Павлоград",
    "Полтава",
    "Ровно",
    "Северодонецк",
    "Северск",
    "Славянск",
    "Стаханов",
    "Сумы",
    "Тернополь",
    "Ужгород",
    "Умань",
    "Фастов",
    "Харьков",
    "Херсон",
    "Черкассы",
    "Черновцы",
    "Чернигов",
    "Червоноград",
    "Шостка",
    "Ялта"
]
truck_types = [
    "🚛 Тент/фура",
    "❄️ Рефрижератор",
    "🧊 Изотерм",
    "🛻 Открытая платформа",
    "🛢️ Автоцистерна",
    "📦 Контейнеровоз",
    "🔻 Низкорамный трал",
    "⛏️ Самосвальный полуприцеп",
    "🪵 Лесовоз",
    "🌾 Зерновоз",
    "🐄 Животновоз",
    "🚗 Автовоз",
    "♻️ Мультилифт",
    "🏗️ Тяжеловоз",
    "🧪 Цементовоз",
    "🔥 Газовоз",
    "🥛 Молоковоз",
    "📃 Площадка без бортов",
    "🛠️ Спецтехника перевозка",
    "🛎️ Туристический автобус",
    "🏍️ Мототранспорт перевозка",
    "📯 Перевозка опасных грузов (ADR)",
    "🧱 Перевозка строительных материалов"
]
payment_methods = [
    "💵 Наличные",
    "💳 Безналичные",
    "💸 Перевод",
    "🏦 Банковский перевод",
    "💱 Криптовалюта",
    "📱 Мобильные платежи",
    "💻 Онлайн-оплата",
    "🌍 Международный перевод",
    "💳 Кредитная карта",
    "📲 Оплата через приложение",
    "🛒 Оплата через интернет-магазин",
    "🏧 Снятие через банкомат",
    "🎁 Оплата бонусами",
    "🧾 Оплата чеками",
    "📤 Оплата через электронные кошельки",
    "💼 Оплата через бизнес-счёт",
    "🔁 Обмен валют",
    "📜 Оплата по договору",
    "🏠 Оплата через кассу",
    "🔒 Безопасная оплата",
    "🎉 Акции/скидки на оплату"
]
currency_methods = [
    "USD 🇺🇸", "EUR 🇪🇺", "UAH 🇺🇦", "GBP 🇬🇧",
    "PLN 🇵🇱", "CHF 🇨🇭", "CAD 🇨🇦", "AUD 🇦🇺",
    "CNY 🇨🇳", "JPY 🇯🇵", "TRY 🇹🇷", "AED 🇦🇪",
    "SEK 🇸🇪", "NOK 🇳🇴", "CZK 🇨🇿", "HUF 🇭🇺",
    "ILS 🇮🇱", "SGD 🇸🇬", "INR 🇮🇳", "BRL 🇧🇷",
    "MXN 🇲🇽", "KRW 🇰🇷", "SAR 🇸🇦", "ZAR 🇿🇦",
    "RUB 🇷🇺", "MYR 🇲🇾", "PHP 🇵🇭", "THB 🇹🇭",
    "IDR 🇮🇩", "EGP 🇪🇬", "PKR 🇵🇰", "TWD 🇹🇼",
    "COP 🇨🇴", "NGN 🇳🇬", "VND 🇻🇳", "UAH 🇺🇦"
]


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация хранилища временных данных
user_data = {}

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить груз")],
        [KeyboardButton(text="👀 Мои грузы")]
    ],
    resize_keyboard=True
)

# Меню подтверждения действий
confirm_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
    ],
    resize_keyboard=True
)

# Меню редактирования
edit_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Название"), KeyboardButton(text="🚛 Отправление")],
        [KeyboardButton(text="📍 Назначение"), KeyboardButton(text="🏢 Компания")],
        [KeyboardButton(text="📞 Телефон"), KeyboardButton(text="💰 Оплата")],
        [KeyboardButton(text="🚛 Тип транспорта"), KeyboardButton(text="💳 Способ оплаты")],
        [KeyboardButton(text="📝 Комментарий"), KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

# Меню выбора типа транспорта
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

truck_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=truck)] for truck in sorted(truck_types)],
    resize_keyboard=True
)

# Меню выбора способа оплаты
payment_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=payment)] for payment in sorted(payment_methods)],
    resize_keyboard=True
)

ukraine_cities_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=city)] for city in sorted(ukraine_cities)],
    resize_keyboard=True
)
# ukraine_cities_menu.add(KeyboardButton(text="🔙 Назад"))

# Меню выбора валюты
currency_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=currency)] for currency in sorted(currency_methods)],
    resize_keyboard=True
)



def format_cargo_data(cargo: Cargo) -> str:
    """Форматирование данных груза для отображения"""
    return (
        f"📦 Название: {cargo.name}\n"
        f"🚛 Отправление: {cargo.origin}\n"
        f"📍 Назначение: {cargo.destination}\n"
        f"🏢 Компания: {cargo.company.company_name if cargo.company else 'Не указано'}\n"
        f"📞 Телефон: {cargo.phone}\n"
        f"💰 Оплата: {cargo.payment} {cargo.currency}\n"
        f"🚛 Тип транспорта: {cargo.truck}\n"
        f"💳 Способ оплаты: {cargo.payment_method}\n"
        f"📝 Комментарий: {cargo.description}\n"
        f"🔑 Номер перевозки: {cargo.shipment_id}"
    )


def hash_data(data: str) -> str:
    return hashlib.sha256((data + SALT).encode()).hexdigest()


@sync_to_async
def get_or_create_user(tg_user: types.User):
    """Получает или создает пользователя Django"""
    try:
        user = User.objects.get(id=tg_user.id)
    except User.DoesNotExist:
        username = tg_user.username or f"tg_user_{tg_user.id}"
        user = User.objects.create_user(
            id=tg_user.id,
            username=username,
            email=f"{username}@example.com",
            password=str(uuid.uuid4()),
            first_name=tg_user.first_name or '',
            last_name=tg_user.last_name or '',
            role='manager'
        )
    return user


@sync_to_async
def get_cargo_by_id(shipment_id: str, user_id: int) -> Cargo:
    """Получение груза по ID"""
    try:
        cargo = Cargo.objects.get(shipment_id=shipment_id, user_id=user_id)
        return cargo
    except Cargo.DoesNotExist:
        logger.warning(f"Груз не найден: shipment_id={shipment_id}")
        raise ValueError("Груз не найден или у вас нет прав доступа.")


@sync_to_async
def get_user_cargos(user_id: int) -> list:
    """Получение всех грузов пользователя"""
    return list(Cargo.objects.filter(user_id=user_id).select_related('company'))


async def save_cargo_to_db(user_id: int, data: dict):
    """Сохранение груза в БД"""
    try:
        # Получаем пользователя
        user = User.objects.get(id=user_id)

        # Пытаемся получить менеджера для автоматического заполнения компании и телефона
        manager = None
        try:
            manager = Manager.objects.get(user=user)
        except Manager.DoesNotExist:
            pass

        # Создаем груз
        cargo = Cargo.objects.create(
            name=data['name'],
            origin=data['origin'],
            destination=data['destination'],
            description=data['description'],
            phone=data['phone'],
            payment=data['payment'],
            currency=data.get('currency', 'USD'),
            truck=data.get('truck', 'Тент/фура'),
            payment_method=data.get('payment_method', 'Наличные'),
            user=user,
            company=data.get('company_obj'),
            created_at=data.get('created_at', timezone.now())
        )

        # Отправляем в группу водителей и сохраняем message_id
        message_id = await send_to_drivers_channel(cargo)
        if message_id:
            cargo.message_id = message_id
            cargo.save()

        return cargo
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        raise


@sync_to_async
def delete_cargo_from_db(shipment_id: str, user_id: int):
    """Удаление груза из БД и соответствующего сообщения в группе"""
    try:
        cargo = Cargo.objects.get(shipment_id=shipment_id, user_id=user_id)
        message_id = cargo.message_id
        cargo.delete()
        return message_id  # Возвращаем ID сообщения для удаления
    except Cargo.DoesNotExist:
        logger.warning(f"Груз не найден для удаления: {shipment_id}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при удалении груза: {e}")
        raise



def update_cargo_field_sync(shipment_id: str, user_id: int, field: str, value):
    """Обновление поля груза (синхронная функция для sync_to_async)"""
    try:
        cargo = Cargo.objects.get(shipment_id=shipment_id, user_id=user_id)
        setattr(cargo, field, value)
        cargo.save()
        return cargo
    except Cargo.DoesNotExist:
        raise ValueError("Груз не найден")
    except Exception as e:
        logger.error(f"Ошибка обновления груза: {e}")
        raise

update_cargo_field = sync_to_async(update_cargo_field_sync)


async def send_to_drivers_channel(cargo: Cargo):
    """Отправка сообщения о грузе в канал для водителей"""
    driver_message = (
        f"🚛 Новый груз доступен!\n\n"
        f"📦 Груз: {cargo.name}\n"
        f"📍 Маршрут: {cargo.origin} → {cargo.destination}\n"
        f"🏢 Компания: {cargo.company.company_name if cargo.company else 'Не указано'}\n"
        f"💰 Оплата: {cargo.payment} {cargo.currency}\n"
        f"🚛 Тип транспорта: {cargo.truck}\n"
        f"💳 Способ оплаты: {cargo.payment_method}\n"
        f"📞 Контакт: {cargo.phone}\n"
        f"📝 Детали: {cargo.description}\n"
        f"🔑 Номер: {str(cargo.shipment_id)[:5]}"
    )

    builder = InlineKeyboardBuilder()
    if cargo.phone.startswith('@'):
        builder.button(text="📨 Написать", url=f"https://t.me/{cargo.phone[1:]}")
    else:
        clean_phone = re.sub(r'[^\d]', '', cargo.phone)
        builder.button(text="📞 Позвонить", url=f"https://t.me/share/phone?phone={clean_phone}")

    try:
        sent_message = await bot.send_message(
            chat_id=DRIVERS_GROUP_ID,
            text=driver_message,
            reply_markup=builder.as_markup()
        )
        # Сохраняем ID сообщения в базе
        await sync_to_async(cargo.save)()
        return sent_message.message_id
    except Exception as e:
        logger.error(f"Ошибка отправки водителям: {e}")
        return None


# Обработчики команд
@dp.message(Command("start"))
async def start(message: Message):
    # Создаем/получаем пользователя в Django
    user = await get_or_create_user(message.from_user)

    await message.answer(
        f"👋 Привет, {user.first_name or user.username}! Выберите действие:",
        reply_markup=main_menu
    )


@dp.message(lambda message: message.text == "➕ Добавить груз")
async def add_cargo(message: Message):
    user_data[message.from_user.id] = {"state": "adding", "data": {}}
    await message.answer("Введите название груза:")


@dp.message(lambda message: message.text == "👀 Мои грузы")
async def show_cargos(message: Message):
    user_id = message.from_user.id
    cargos = await get_user_cargos(user_id)

    if not cargos:
        await message.answer("У вас нет сохраненных грузов.")
        return

    await message.answer("📦 Ваши грузы:")

    for cargo in cargos:
        msg = (
            f"📦 Название: {cargo.name}\n"
            f"🚚 Маршрут: {cargo.origin} → {cargo.destination}\n"
            f"🚛 Тип транспорта: {cargo.truck}\n"
            f"💵 Оплата: {cargo.payment} {cargo.currency}"
            f"💳 Способ оплаты: {cargo.payment_method}\n"
            f"📝 Комментарий: {cargo.description}\n"
            f"🔑 Номер перевозки: {cargo.shipment_id}"
        )

        builder = InlineKeyboardBuilder()
        builder.button(text="✏ Редактировать", callback_data=f"edit_{cargo.shipment_id}")
        builder.button(text="🗑 Удалить", callback_data=f"delete_{cargo.shipment_id}")

        await message.answer(msg, reply_markup=builder.as_markup())


@dp.callback_query(lambda c: c.data.startswith('delete_'))
async def delete_cargo(callback: CallbackQuery):
    shipment_id = callback.data.replace('delete_', '')
    user_id = callback.from_user.id

    try:
        message_id = await delete_cargo_from_db(shipment_id, user_id)
        if message_id is not None:
            # Пытаемся удалить сообщение из группы водителей
            try:
                await bot.delete_message(chat_id=DRIVERS_GROUP_ID, message_id=message_id)
            except TelegramBadRequest as e:
                if "message to delete not found" in str(e):
                    logger.info("Сообщение уже было удалено")
                elif "message can't be deleted" in str(e):
                    logger.info("Прошло более 48 часов, сообщение нельзя удалить")
                else:
                    logger.warning(f"Ошибка при удалении сообщения: {e}")
            except TelegramAPIError as e:
                logger.error(f"Ошибка API Telegram при удалении сообщения: {e}")

            await callback.answer("Груз удален", show_alert=True)
            await callback.message.delete()
        else:
            await callback.answer("Груз не найден", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
        await callback.answer("Ошибка удаления", show_alert=True)


@dp.callback_query(lambda c: c.data.startswith('edit_'))
async def edit_cargo(callback: CallbackQuery):
    shipment_id = callback.data.replace('edit_', '')
    user_id = callback.from_user.id

    try:
        cargo = await get_cargo_by_id(shipment_id, user_id)
        user_data[user_id] = {
            "state": "editing",
            "data": cargo,
            "shipment_id": shipment_id
        }
        await callback.message.answer(
            "Выберите поле для редактирования:",
            reply_markup=edit_menu
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка редактирования: {e}")
        await callback.answer("Ошибка при редактировании", show_alert=True)


# Обработка редактирования
@dp.message(lambda message: message.text in ["📦 Название", "🚛 Отправление", "📍 Назначение",
                                             "🏢 Компания", "📞 Телефон", "💰 Оплата",
                                             "🚛 Тип транспорта", "💳 Способ оплаты", "📝 Комментарий"])
async def edit_field(message: Message):
    user_id = message.from_user.id
    if user_id not in user_data or user_data[user_id]["state"] != "editing":
        await message.answer("Используйте кнопки меню", reply_markup=main_menu)
        return

    field_map = {
        "📦 Название": "name",
        "🚛 Отправление": "origin",
        "📍 Назначение": "destination",
        "🏢 Компания": "company",
        "📞 Телефон": "phone",
        "💰 Оплата": "payment",
        "🚛 Тип транспорта": "truck",
        "💳 Способ оплаты": "payment_method",
        "📝 Комментарий": "description"
    }

    field = field_map[message.text]
    user_data[user_id]["edit_field"] = field

    if field == "truck":
        await message.answer("Выберите тип транспорта:", reply_markup=truck_menu)
    elif field == "payment_method":
        await message.answer("Выберите способ оплаты:", reply_markup=payment_menu)
    elif field == "payment":
        await message.answer("Введите сумму оплаты:", reply_markup=currency_menu)
    else:
        await message.answer(f"Введите новое значение для {message.text}:", reply_markup=types.ReplyKeyboardRemove())


# Обработка ввода новых значений
@dp.message()
async def handle_input(message: Message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in user_data:
        await message.answer("Используйте кнопки меню", reply_markup=main_menu)
        return

    if user_data[user_id]["state"] == "adding":
        await handle_add_cargo(message)
    elif user_data[user_id]["state"] == "editing" and "edit_field" in user_data[user_id]:
        await handle_edit_field(message)


# async def handle_add_cargo(message: Message):
#     user_id = message.from_user.id
#     text = message.text
#     data = user_data[user_id]["data"]
#
#     if "name" not in data:
#         if 2 <= len(text) <= 100:
#             data["name"] = text
#             await message.answer("Введите пункт отправления:")
#         else:
#             await message.answer("Название должно быть 2-100 символов")
#     elif "origin" not in data:
#         data["origin"] = text
#         await message.answer("Введите пункт назначения:")
#     elif "destination" not in data:
#         data["destination"] = text
#         await message.answer("Введите название компании:")
#     elif "company" not in data:
#         if 2 <= len(text) <= 100:
#             data["company"] = text
#             keyboard = ReplyKeyboardMarkup(
#                 keyboard=[
#                     [KeyboardButton(text="📱 Ввести телефон в формате (+380...)")],
#                     [KeyboardButton(text="📲 Использовать Telegram")]
#                 ],
#                 resize_keyboard=True
#             )
#             await message.answer("Выберите способ контакта:", reply_markup=keyboard)
#         else:
#             await message.answer("Название компании должно быть 2-100 символов")
#     elif "phone" not in data:
#         if message.text == "📲 Использовать Telegram":
#             if message.from_user.username:
#                 data["phone"] = f"@{message.from_user.username}"
#                 await message.answer("Введите сумму оплаты:", reply_markup=currency_menu)
#             else:
#                 await message.answer("У вас нет username. Введите телефон в формате (+380...):")
#         elif re.match(r"^\+?[1-9]\d{1,14}$", text):
#             data["phone"] = text
#             await message.answer("Введите сумму оплаты:", reply_markup=currency_menu)
#         else:
#             await message.answer("Введите корректный телефон в формате (+380...)")
#     elif "payment" not in data:
#         try:
#             payment = float(text)
#             if payment > 0:
#                 data["payment"] = payment
#                 await message.answer("Выберите валюту оплаты:", reply_markup=currency_menu)
#             else:
#                 await message.answer("Сумма должна быть > 0")
#         except ValueError:
#             await message.answer("Введите число")
#     elif "currency" not in data and text in ["USD", "EUR", "UAH"]:
#         data["currency"] = text
#         await message.answer("Выберите тип транспорта:", reply_markup=truck_menu)
#     elif "truck" not in data and text in ["Тент/фура", "Рефрижератор", "Изотерм", "Открытая платформа", "Автоцистерна"]:
#         data["truck"] = text
#         await message.answer("Выберите способ оплаты:", reply_markup=payment_menu)
#     elif "payment_method" not in data and text in ["Наличные", "Безналичные", "Перевод"]:
#         data["payment_method"] = text
#         await message.answer("Введите комментарий:")
#     elif "description" not in data:
#         if len(text) <= 500:
#             data["description"] = text
#
#             try:
#                 # Создаем компанию, если она была указана
#                 company_name = data.get('company')
#                 if company_name:
#                     company, _ = await sync_to_async(Company.objects.get_or_create)(company_name=company_name)
#                     data['company_obj'] = company
#
#                 # Сохраняем груз в БД
#                 cargo = await save_cargo_to_db(user_id, data)
#
#                 # Отправляем уведомление водителям
#                 await send_to_drivers_channel(cargo)
#
#                 await message.answer(
#                     f"✅ Груз сохранен!\n{format_cargo_data(cargo)}",
#                     reply_markup=main_menu
#                 )
#                 del user_data[user_id]
#             except Exception as e:
#                 logger.error(f"Ошибка сохранения: {e}")
#                 await message.answer("Ошибка сохранения", reply_markup=main_menu)
#         else:
#             await message.answer("Комментарий слишком длинный (макс 500 симв)")
async def handle_add_cargo(message: Message):
    user_id = message.from_user.id
    text = message.text
    data = user_data[user_id]["data"]

    if "name" not in data:
        if 2 <= len(text) <= 100:
            data["name"] = text
            await message.answer("Выберите пункт отправления:", reply_markup=ukraine_cities_menu)
        else:
            await message.answer("Название должно быть 2-100 символов")
    elif "origin" not in data:
        # Проверяем, что выбранный город есть в списке допустимых городов
        if text in ukraine_cities:  # Проверяем, что выбран город из списка
            data["origin"] = text
            await message.answer("Выберите пункт назначения:", reply_markup=ukraine_cities_menu)
        else:
            await message.answer("Пожалуйста, выберите город из кнопок", reply_markup=ukraine_cities_menu)
    elif "destination" not in data:
        if text in ukraine_cities:  # Проверяем, что выбран город из списка
            data["destination"] = text
            await message.answer("Введите название компании:")
        else:
            await message.answer("Пожалуйста, выберите город из кнопок", reply_markup=ukraine_cities_menu)
    elif "company" not in data:
        if 2 <= len(text) <= 100:
            data["company"] = text
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📱 Ввести телефон в формате (+380...)")],
                    [KeyboardButton(text="📲 Использовать Telegram")]
                ],
                resize_keyboard=True
            )
            await message.answer("Выберите способ контакта:", reply_markup=keyboard)
        else:
            await message.answer("Название компании должно быть 2-100 символов")
    elif "phone" not in data:
        if text == "📲 Использовать Telegram":
            if message.from_user.username:
                data["phone"] = f"@{message.from_user.username}"
                await message.answer("Введите сумму оплаты:", reply_markup=currency_menu)
            else:
                await message.answer("У вас нет username. Введите телефон в формате (+380...):")
        elif re.match(r"^\+?[1-9]\d{1,14}$", text):
            data["phone"] = text
            await message.answer("Введите сумму оплаты:") #, reply_markup=currency_menu
        else:
            await message.answer("Введите корректный телефон в формате (+380...)")
    elif "payment" not in data:
        try:
            payment = float(text)
            if payment > 0:
                data["payment"] = payment
                await message.answer("Выберите валюту оплаты:", reply_markup=currency_menu)
            else:
                await message.answer("Сумма должна быть > 0")
        except ValueError:
            await message.answer("Введите сумму оплати")
    elif "currency" not in data and text in payment_methods:
        data["currency"] = text
        await message.answer("Выберите тип транспорта:", reply_markup=truck_menu)
    elif "truck" not in data and text in truck_types:
        data["truck"] = text
        await message.answer("Выберите способ оплаты:", reply_markup=payment_menu)
    elif "payment_method" not in data and text in currency_methods:
        data["payment_method"] = text
        await message.answer("Введите комментарий:")
    elif "description" not in data:
        if len(text) <= 500:
            data["description"] = text

            try:
                # Создаем компанию, если указана
                company_name = data.get('company')
                if company_name:
                    company, _ = await sync_to_async(Company.objects.get_or_create)(company_name=company_name)
                    data['company_obj'] = company

                # Сохраняем груз в БД
                cargo = await save_cargo_to_db(user_id, data)

                # Отправляем уведомление водителям
                await send_to_drivers_channel(cargo)

                await message.answer(
                    f"✅ Груз сохранен!\n{format_cargo_data(cargo)}",
                    reply_markup=main_menu
                )
                del user_data[user_id]
            except Exception as e:
                logger.error(f"Ошибка сохранения: {e}")
                await message.answer("Ошибка сохранения", reply_markup=main_menu)
        else:
            await message.answer("Комментарий слишком длинный (макс 500 символов)")

async def handle_edit_field(message: Message):

        user_id = message.from_user.id
        text = message.text
        field = user_data[user_id]["edit_field"]
        shipment_id = user_data[user_id]["shipment_id"]

        # Валидация ввода
        valid = True
        if field == "name" and not (2 <= len(text) <= 100):
            await message.answer("Название должно быть 2-100 символов")
            valid = False
        elif field == "company" and not (2 <= len(text) <= 100):
            await message.answer("Название компании должно быть 2-100 символов")
            valid = False
        elif field == "phone" and not re.match(r"^\+?[1-9]\d{1,14}$", text) and not text.startswith("@"):
            await message.answer("Введите корректный телефон или @username")
            valid = False
        elif field == "payment":
            try:
                amount = float(text)
                if amount <= 0:
                    await message.answer("Сумма должна быть > 0")
                    valid = False
                else:
                    text = amount
            except ValueError:
                await message.answer("Введите число")
                valid = False
        elif field == "description" and len(text) > 500:
            await message.answer("Комментарий слишком длинный (макс 500 симв)")
            valid = False
        elif field == "truck" and text not in ["Тент/фура", "Рефрижератор", "Изотерм", "Открытая платформа", "Автоцистерна"]:
            await message.answer("Выберите тип транспорта из меню")
            valid = False
        elif field == "payment_method" and text not in ["Наличные", "Безналичные", "Перевод"]:
            await message.answer("Выберите способ оплаты из меню")
            valid = False
        elif field == "currency" and text not in ["USD", "EUR", "UAH"]:
            await message.answer("Выберите валюту из меню")
            valid = False

        if not valid:
            return

        try:
            if field == "company":
                # Закрываем старые соединения перед записью
                await sync_to_async(close_old_connections)()
                company_obj, _ = await sync_to_async(Company.objects.get_or_create)(company_name=text)
                await sync_to_async(close_old_connections)()
                cargo = await update_cargo_field(shipment_id, user_id, 'company', company_obj)
                await message.answer(
                    f"✅ Поле успешно обновлено!\n{format_cargo_data(cargo)}",
                    reply_markup=main_menu
                )
                del user_data[user_id]
                return
            else:
                # Закрываем старые соединения перед записью
                await sync_to_async(close_old_connections)()
                cargo = await update_cargo_field(shipment_id, user_id, field, text)
                await message.answer(
                    f"✅ Поле успешно обновлено!\n{format_cargo_data(cargo)}",
                    reply_markup=main_menu
                )
                del user_data[user_id]
        except Exception as e:
            logger.error(f"Ошибка обновления: {e}")
            await message.answer(f"✅ Поле успешно обновлено!", reply_markup=main_menu)


async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())