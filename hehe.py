

import asyncio
import datetime
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import config
import database

# Определяем класс состояний (FSM)
class FSMClient(StatesGroup):
    waiting_image_prompt = State()
    waiting_research_query = State()
    waiting_extra_messages = State()
    waiting_extra_images = State()
    waiting_extra_videos = State()

def get_referrals(user_id: int) -> int:
    """Возвращает количество пользователей, приглашённых данным пользователем."""
    import sqlite3
    # Подключаемся к базе данных и получаем количество рефералов
    conn = sqlite3.connect("database.db")  # путь к файлу базы данных, если отличается – отредактируйте
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE ref_by=?", (user_id,))
    count = cur.fetchone()[0] or 0
    conn.close()
    return count

async def main_menu() -> types.ReplyKeyboardMarkup:
    """Формирует и возвращает разметку клавиатуры главного меню."""
    kb = ReplyKeyboardBuilder()
    kb.row(
        types.KeyboardButton(text="Мои приглашенные"),
        types.KeyboardButton(text="Моя подписка")
    )
    kb.row(
        types.KeyboardButton(text="Генерация изображений"),
        types.KeyboardButton(text="Глубокое исследование")
    )
    kb.row(
        types.KeyboardButton(text="Премиум бесплатно"),
        types.KeyboardButton(text="Помощь")
    )
    return kb.as_markup(resize_keyboard=True)

# Инициализируем роутер для хендлеров
router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """Обрабатывает команду /start: приветствие, начальная регистрация и меню."""
    # Сбрасываем состояние пользователя, если он был в середине диалога
    await state.clear()
    user = message.from_user
    user_id = user.id
    # Проверяем, есть ли аргумент (реферальный код) после команды /start
    args = message.text.split()
    referrer_id = None
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
        except ValueError:
            referrer_id = None
    # Сохраняем пользователя в базе (если необходимо) с указанием кто его пригласил
    # Например:
    # database.add_user(user_id, ref_by=referrer_id, name=user.full_name, join_date=datetime.datetime.now())
    # (Предполагается, что в модуле database реализована подобная функция или логика добавления)
    # Формируем приветственное сообщение
    name = user.first_name if user.first_name else "друг"
    welcome_text = (
        f"Привет, {name}!\n"
        "Добро пожаловать в бота.\n"
        "Здесь вы можете генерировать изображения и проводить глубокое исследование.\n"
        "Используйте меню ниже для выбора действия."
    )
    # Отправляем приветствие и отображаем меню
    await message.answer(welcome_text, reply_markup=await main_menu())

@router.message(F.text == "Мои приглашенные", F.state == None)
async def my_invites(message: types.Message):
    """Обрабатывает нажатие кнопки 'Мои приглашенные': выводит количество рефералов."""
    user_id = message.from_user.id
    count = get_referrals(user_id)
    await message.answer(f"Вы пригласили {count} пользователей.")

@router.message(F.text == "Моя подписка", F.state == None)
async def my_subscription(message: types.Message):
    """Обрабатывает нажатие кнопки 'Моя подписка': показывает статус текущего тарифа."""
    current_plan = "Light"  # допустим, базовый тариф называется "Light"
    await message.answer(
        f"Ваш текущий тариф: {current_plan}.\n"
        "Чтобы получить премиум, вы можете пригласить друзей."
    )

@router.message(F.text == "Генерация изображений", F.state == None)
async def start_image_generation(message: types.Message, state: FSMContext):
    """Обрабатывает нажатие 'Генерация изображений': начинает сценарий запроса описания."""
    await state.set_state(FSMClient.waiting_image_prompt)
    await message.answer(
        "Пожалуйста, отправьте описание изображения для генерации.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text == "Глубокое исследование", F.state == None)
async def start_deep_research(message: types.Message, state: FSMContext):
    """Обрабатывает нажатие 'Глубокое исследование': начинает сценарий запроса темы."""
    await state.set_state(FSMClient.waiting_research_query)
    await message.answer(
        "Введите тему, которую вы хотите исследовать.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(FSMClient.waiting_image_prompt)
async def process_image_prompt(message: types.Message, state: FSMContext):
    """Обрабатывает введённый пользователем запрос для генерации изображения."""
    prompt = message.text
    # (Здесь могла бы выполняться логика генерации изображения — не реализовано)
    # Завершаем FSM и уведомляем пользователя
    await state.clear()
    await message.answer(
        "Ваш запрос на генерацию изображения принят.\n"
        "(Функция генерации пока не реализована.)",
        reply_markup=await main_menu()
    )

@router.message(FSMClient.waiting_research_query)
async def process_research_query(message: types.Message, state: FSMContext):
    """Обрабатывает введённую тему для глубокого исследования, запрашивает количество текстов."""
    topic = message.text
    # Сохраняем тему исследования во временном хранилище FSM
    await state.update_data(topic=topic)
    # Переходим к следующему шагу: запрашиваем количество текстовых материалов
    await state.set_state(FSMClient.waiting_extra_messages)
    await message.answer("Сколько текстовых материалов включить в исследование?")

@router.message(FSMClient.waiting_extra_messages)
async def process_extra_messages(message: types.Message, state: FSMContext):
    """Обрабатывает количество текстовых материалов и запрашивает количество изображений."""
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    extra_messages = int(message.text)
    await state.update_data(extra_messages=extra_messages)
    # Переходим к следующему шагу: запрашиваем количество изображений
    await state.set_state(FSMClient.waiting_extra_images)
    await message.answer("Сколько изображений включить в исследование?")

@router.message(FSMClient.waiting_extra_images)
async def process_extra_images(message: types.Message, state: FSMContext):
    """Обрабатывает количество изображений и запрашивает количество видео."""
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    extra_images = int(message.text)
    await state.update_data(extra_images=extra_images)
    # Переходим к следующему шагу: запрашиваем количество видео
    await state.set_state(FSMClient.waiting_extra_videos)
    await message.answer("Сколько видео включить в исследование?")

@router.message(FSMClient.waiting_extra_videos)
async def process_extra_videos(message: types.Message, state: FSMContext):
    """Обрабатывает количество видео и завершает сценарий глубокого исследования."""
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    extra_videos = int(message.text)
    data = await state.get_data()
    topic = data.get("topic", "")
    extra_messages = data.get("extra_messages", 0)
    extra_images = data.get("extra_images", 0)
    # Завершаем FSM и формируем ответ (имитация результата исследования)
    await state.clear()
    result_text = (
        f"Запрос на исследование по теме «{topic}» принят.\n"
        f"Текстовых материалов: {extra_messages}, изображений: {extra_images}, видео: {extra_videos}.\n"
        f"(Функция глубокого исследования пока не реализована.)"
    )
    await message.answer(result_text, reply_markup=await main_menu())

@router.message(F.text == "Премиум бесплатно", F.state == None)
async def premium_free_info(message: types.Message):
    """Обрабатывает нажатие 'Премиум бесплатно': условия получения премиума."""
    user_id = message.from_user.id
    count = get_referrals(user_id)
    # Предполагаем, что для бесплатного премиума нужно пригласить 5 пользователей
    needed = 5
    if count >= needed:
        text = (
            "Поздравляем! Вы пригласили достаточное количество пользователей для получения премиума бесплатно.\n"
            "Ваш аккаунт будет переведён на премиум-доступ."
        )
    else:
        remaining = needed - count
        text = (
            f"Чтобы получить премиум бесплатно, пригласите {needed} друзей по вашей реферальной ссылке.\n"
            f"Вы уже пригласили: {count}. Осталось пригласить: {remaining}."
        )
    await message.answer(text)

@router.message(F.text == "Помощь", F.state == None)
async def send_help(message: types.Message):
    """Обрабатывает нажатие 'Помощь': выводит информацию о функционале бота."""
    help_text = (
        "Бот предоставляет следующие возможности:\n"
        "- Генерация изображений по описанию.\n"
        "- Глубокое поиск информации по теме.\n\n"
        "Используйте меню для выбора действия.\n"
        "Приглашайте друзей, чтобы получить премиум доступ."
    )
    await message.answer(help_text)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=config.API_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())
    # Регистрируем роутер с хендлерами
    dp.include_router(router)
    # Удаляем вебхук и пропускаем накопленные обновления при запуске
    await bot.delete_webhook(drop_pending_updates=True)
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Инициализация базы данных (например, создание таблиц)
    database.init_db()
    # Запуск бота
    asyncio.run(main())
