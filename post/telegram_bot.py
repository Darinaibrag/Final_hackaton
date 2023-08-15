import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from django.core.management.base import BaseCommand
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import aiohttp
import tempfile
import os
from urllib.parse import urljoin
from aiogram.types import ReplyKeyboardRemove
import asyncio

# URL эндпоинта API
HOTEL_API_URL_RANDOM = "http://127.0.0.1:8000/post/hotel-random/"
TOUR_API_URL_RANDOM = "http://127.0.0.1:8000/post/tour-random/"
TOP_RATED_HOTELS_API_URL = "http://127.0.0.1:8000/post/hotel-next/"
ACTIVITY_TYPE_TOUR_API_URL = "http://127.0.0.1:8000/post/tour-next/"

API_TOKEN = "6012004719:AAFwyJYzUxhlBj9y-7XMWUxVdEtTFtJfh44"

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class UserState(StatesGroup):
    start = State()  # Состояние начала диалога
    hotel = State()  # Состояние выбора отеля
    tour = State()  # Состояние выбора тура
    exiting = State()  # Состояние выхода
    regions_menu = State()


# Handle the /start command
@dispatcher.message_handler(Command('start'), state="*")
async def start_command(message: types.Message, state: FSMContext):
    # Создаем клавиатуру с кнопками
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('📞 Служба поддержки')
    button2 = KeyboardButton('🚀 Ключевые области')
    button3 = KeyboardButton('❌ Выйти из бота')
    keyboard.add(button1, button2, button3)

    # Отправляем приветственное сообщение и клавиатуру
    welcome_message = ("Добро пожаловать в kayakta_bot!\n"
                       "Мы гордимся природой Кыргызстана, и хотим пригласить вас увидеть всю красоту нашей страны своими собственными глазами!\n"
                       "Моя цель - подобрать вам самый подходящий тур и отель для поездки в Кыргызстан.\n"
                       "Наша программа включает в себя следующие ключевые области:")

    await message.reply(welcome_message, reply_markup=keyboard)
    await UserState.start.set()


@dispatcher.message_handler(lambda message: message.text == '📞 Служба поддержки', state="*")
async def support_command(message: types.Message, state: FSMContext):
    support_message = (
        "Добрый день!\n"
        "Электронная почта для связи: kaykta_support@gmail.com"
    )
    await message.answer(support_message)
    await state.finish()

@dispatcher.message_handler(lambda message: message.text == '❌ Выйти из бота', state="*")
async def exit_bot(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()  # Создаем объект для удаления клавиатуры
    await message.reply("Вы выбрали '❌ Выйти из бота'. До свидания!", reply_markup=markup)
    await bot.close()  # Закрываем соединение с Telegram API
    await state.finish()



# Обработчик кнопки "🚀 Ключевые области"
@dispatcher.message_handler(lambda message: message.text == '🚀 Ключевые области', state="*")
async def regions_command(message: types.Message, state: FSMContext):
    # Создаем клавиатуру с выбором отелей и туров
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    hotels_button = KeyboardButton('🏨 Отели в Бишкеке')
    tours_button = KeyboardButton('🌄 Туры по Кыргызстану')
    back_button = KeyboardButton('⬅️ Назад')
    markup.add(hotels_button, tours_button, back_button)

    await message.answer("Выберите одну из следующих опций:", reply_markup=markup)

    # Устанавливаем состояние regions_menu для отслеживания выбора между отелями и турами
    await UserState.regions_menu.set()

# Обработчик выбора "🏨 Отели в Бишкеке"
@dispatcher.message_handler(lambda message: message.text == '🏨 Отели в Бишкеке', state=UserState.regions_menu)
async def hotels_command(message: types.Message, state: FSMContext):
    # Создаем клавиатуру с выбором отелей в Бишкеке
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    by_rating_button = KeyboardButton('🔝 По рейтингу отелей')
    random_hotel_button = KeyboardButton('🎲 Случайный отель')
    back_button = KeyboardButton('⬅️ Назад')
    markup.add(by_rating_button, random_hotel_button, back_button)

    await message.answer("Выберите способ выбора отеля:", reply_markup=markup)

    # Устанавливаем состояние для выбора варианта отелей в Бишкеке
    await UserState.hotel.set()


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# ...

from aiogram.dispatcher import FSMContext

# Обработчик выбора "🔝 По рейтингу отелей"
@dispatcher.message_handler(lambda message: message.text == '🔝 По рейтингу отелей', state=UserState.hotel)
async def top_rated_hotels_command(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(TOP_RATED_HOTELS_API_URL) as response:
                if response.status == 200:
                    hotels_data = await response.json()
                    results = hotels_data.get("results", {})
                    next_link = hotels_data.get("next")
                    previous_link = hotels_data.get("previous")

                    title = results.get("title", "Название неизвестно")
                    relative_preview = results.get("preview", "")
                    price = results.get("price", "Цена не указана")
                    avg_rating = results.get("rating", {}).get("avg_rating", "Рейтинг отсутствует")
                    rating_count = results.get("rating", {}).get("rating_count", 0)

                    full_preview_url = urljoin(HOTEL_API_URL_RANDOM, relative_preview)

                    # Скачиваем изображение и сохраняем его как временный файл
                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    hotel_info = (
                        f"🏨 Отель: {title}\n"
                        f"💰 Цена: {price} сом\n"
                        f"⭐ Рейтинг: {avg_rating} (Отзывов: {rating_count})"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await message.answer_photo(photo=types.InputFile(photo_file), caption=hotel_info)

                    os.remove(temp_image_path)  # Удаляем временный файл

                    # Создаем кнопки для перехода к следующему и предыдущему посту
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if hotels_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_page_hotels"))
                    if hotels_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_page_hotels"))

                    await message.answer("Выберите действие:", reply_markup=keyboard)

                else:
                    await message.answer("Извините, произошла ошибка при получении данных об отелях.")
        except Exception as e:
            await message.answer("Извините, произошла ошибка при получении данных об отелях.")
            print(str(e))  # Выводим ошибку для отладки


@dispatcher.callback_query_handler(lambda query: query.data == "next_page_hotels", state=UserState.hotel)
async def next_page_hotels_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            data = await state.get_data()
            next_link = data.get("next_link")

            async with session.get(next_link) as response:
                if response.status == 200:
                    hotels_data = await response.json()
                    results = hotels_data.get("results", {})
                    next_link = hotels_data.get("next")
                    previous_link = hotels_data.get("previous")

                    title = results.get("title", "Название неизвестно")
                    relative_preview = results.get("preview", "")
                    price = results.get("price", "Цена не указана")
                    avg_rating = results.get("rating", {}).get("avg_rating", "Рейтинг отсутствует")
                    rating_count = results.get("rating", {}).get("rating_count", 0)

                    full_preview_url = urljoin(HOTEL_API_URL_RANDOM, relative_preview)

                    # Скачиваем изображение и сохраняем его как временный файл
                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    hotel_info = (
                        f"🏨 Отель: {title}\n"
                        f"💰 Цена: {price} сом\n"
                        f"⭐ Рейтинг: {avg_rating} (Отзывов: {rating_count})"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await bot.send_photo(callback_query.message.chat.id, photo=photo_file, caption=hotel_info)

                    os.remove(temp_image_path)

                    # Обновляем инлайн-клавиатуру для следующей страницы
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if hotels_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_page_hotels"))
                    if hotels_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_page_hotels"))

                    await bot.send_message(callback_query.message.chat.id, "Выберите действие:", reply_markup=keyboard)
                    # await callback_query.message.edit_reply_markup(reply_markup=keyboard)

                else:
                    await callback_query.message.answer("Извините, произошла ошибка при получении данных об отелях.")
        except Exception as e:
            await callback_query.message.answer("Извините, произошла ошибка при получении данных об отелях.")
            print(str(e))


@dispatcher.callback_query_handler(lambda query: query.data == "previous_page_hotels", state=UserState.hotel)
async def previous_page_hotels_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            data = await state.get_data()
            previous_link = data.get("previous_link")

            async with session.get(previous_link) as response:
                if response.status == 200:
                    hotels_data = await response.json()
                    results = hotels_data.get("results", {})
                    next_link = hotels_data.get("next")
                    previous_link = hotels_data.get("previous")

                    title = results.get("title", "Название неизвестно")
                    relative_preview = results.get("preview", "")
                    price = results.get("price", "Цена не указана")
                    avg_rating = results.get("rating", {}).get("avg_rating", "Рейтинг отсутствует")
                    rating_count = results.get("rating", {}).get("rating_count", 0)

                    full_preview_url = urljoin(HOTEL_API_URL_RANDOM, relative_preview)

                    # Скачиваем изображение и сохраняем его как временный файл
                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    hotel_info = (
                        f"🏨 Отель: {title}\n"
                        f"💰 Цена: {price} сом\n"
                        f"⭐ Рейтинг: {avg_rating} (Отзывов: {rating_count})"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await bot.send_photo(callback_query.message.chat.id, photo=photo_file, caption=hotel_info)

                    os.remove(temp_image_path)  # Удаляем временный файл


                    # Обновляем инлайн-клавиатуру для следующей страницы
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if hotels_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_page_hotels"))
                    if hotels_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_page_hotels"))

                    await bot.send_message(callback_query.message.chat.id, "Выберите действие:", reply_markup=keyboard)
                    # await callback_query.message.edit_reply_markup(reply_markup=keyboard)

                else:
                    await callback_query.message.answer("Извините, произошла ошибка при получении данных об отелях.")
        except Exception as e:
            await callback_query.message.answer("Извините, произошла ошибка при получении данных об отелях.")
            print(str(e))


@dispatcher.message_handler(lambda message: message.text == '🎲 Случайный отель', state=UserState.hotel)
async def random_hotel_command(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(HOTEL_API_URL_RANDOM) as response:
                if response.status == 200:
                    hotel_data = await response.json()
                    title = hotel_data.get("title", "Название неизвестно")
                    relative_preview = hotel_data.get("preview", "")
                    price = hotel_data.get("price", "Цена не указана")
                    rating = hotel_data.get("rating", {}).get("rating__avg", "Рейтинг отсутствует")
                    rating_count = hotel_data.get("rating", {}).get("rating_count", 0)

                    full_preview_url = urljoin(HOTEL_API_URL_RANDOM, relative_preview)

                    # Скачиваем изображение и сохраняем его как временный файл
                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    hotel_info = (
                        f"🏨 Отель: {title}\n"
                        f"💰 Цена: {price} сом\n"
                        f"⭐ Рейтинг: {rating} (Отзывов: {rating_count})"
                    )

                    with open(temp_image_path, 'rb') as photo_file:
                        await message.answer_photo(photo=types.InputFile(photo_file), caption=hotel_info)

                    os.remove(temp_image_path)  # Удаляем временный файл
                else:
                    await message.answer("Извините, произошла ошибка при получении данных об отеле.")
        except Exception as e:
            await message.answer("Извините, произошла ошибка при получении данных об отеле.")
            print(str(e))  # Выводим ошибку для отладки




# Обработчик выбора "🌄 Туры по Кыргызстану"
@dispatcher.message_handler(lambda message: message.text == '🌄 Туры по Кыргызстану', state=UserState.regions_menu)
async def tours_command(message: types.Message, state: FSMContext):
    # Создаем клавиатуру с выбором туров по Кыргызстану
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    by_type_button = KeyboardButton('🧗‍♂️ По виду активности')
    random_tour_button = KeyboardButton('🎲 Случайный тур')
    back_button = KeyboardButton('⬅️ Назад')
    markup.add(by_type_button, random_tour_button, back_button)

    await message.answer("Выберите способ выбора тура:", reply_markup=markup)

    # Устанавливаем состояние для выбора варианта туров по Кыргызстану
    await UserState.tour.set()


# Обработчик выбора "🧗‍♂️ По виду активности"
@dispatcher.message_handler(lambda message: message.text == '🧗‍♂️ По виду активности', state=UserState.tour)
async def activity_type_tours_command(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(ACTIVITY_TYPE_TOUR_API_URL) as response:
                if response.status == 200:
                    hotels_data = await response.json()
                    results = hotels_data.get("results", {})
                    next_link = hotels_data.get("next")
                    previous_link = hotels_data.get("previous")

                    title = results.get("title", "Название неизвестно")
                    relative_preview = results.get("preview", "")
                    price = results.get("price", "Цена не указана")
                    rating = results.get("rating", {}).get("avg_rating", "Рейтинг отсутствует")
                    rating_count = results.get("rating", {}).get("rating_count", 0)

                    full_preview_url = urljoin(ACTIVITY_TYPE_TOUR_API_URL, relative_preview)

                    # Скачиваем изображение и сохраняем его как временный файл
                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    hotel_info = (
                        f"🌄 Тур: {title}\n"
                        f"💰 Цена: {price} сом\n"
                        f"⭐ Рейтинг: {rating} (Отзывов: {rating_count})"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await message.answer_photo(photo=types.InputFile(photo_file), caption=hotel_info)

                    os.remove(temp_image_path)  # Удаляем временный файл

                    # Создаем кнопки для перехода к следующему и предыдущему посту
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if hotels_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_page_activity"))
                    if hotels_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_page_activity"))

                    await message.answer("Выберите действие:", reply_markup=keyboard)

                else:
                    await message.answer("Извините, произошла ошибка при получении данных об отелях.")
        except Exception as e:
            await message.answer("Извините, произошла ошибка при получении данных об отелях.")
            print(str(e))  # Выводим ошибку для отладки



@dispatcher.callback_query_handler(lambda query: query.data == "next_page_activity", state=UserState.tour)
async def next_page_tours_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            data = await state.get_data()
            next_link = data.get("next_link")

            async with session.get(next_link) as response:
                if response.status == 200:
                    hotels_data = await response.json()
                    results = hotels_data.get("results", {})
                    next_link = hotels_data.get("next")
                    previous_link = hotels_data.get("previous")

                    title = results.get("title", "Название неизвестно")
                    relative_preview = results.get("preview", "")
                    price = results.get("price", "Цена не указана")
                    rating = results.get("rating", {}).get("avg_rating", "Рейтинг отсутствует")
                    rating_count = results.get("rating", {}).get("rating_count", 0)

                    full_preview_url = urljoin(HOTEL_API_URL_RANDOM, relative_preview)

                    # Скачиваем изображение и сохраняем его как временный файл
                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    hotel_info = (
                        f"🌄 Тур: {title}\n"
                        f"💰 Цена: {price} сом\n"
                        f"⭐ Рейтинг: {rating} (Отзывов: {rating_count})"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await bot.send_photo(callback_query.message.chat.id, photo=photo_file, caption=hotel_info)

                    os.remove(temp_image_path)

                    # Обновляем инлайн-клавиатуру для следующей страницы
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if hotels_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_page_activity"))
                    if hotels_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_page_activity"))

                    await bot.send_message(callback_query.message.chat.id, "Выберите действие:", reply_markup=keyboard)
                    # await callback_query.message.edit_reply_markup(reply_markup=keyboard)

                else:
                    await callback_query.message.answer("Извините, произошла ошибка при получении данных о турах.")
        except Exception as e:
            await callback_query.message.answer("Извините, произошла ошибка при получении данных о турах.")
            print(str(e))



@dispatcher.callback_query_handler(lambda query: query.data == "previous_page_activity", state=UserState.tour)
async def previous_page_tours_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            data = await state.get_data()
            previous_link = data.get("previous_link")

            async with session.get(previous_link) as response:
                if response.status == 200:
                    hotels_data = await response.json()
                    results = hotels_data.get("results", {})
                    next_link = hotels_data.get("next")
                    previous_link = hotels_data.get("previous")

                    title = results.get("title", "Название неизвестно")
                    relative_preview = results.get("preview", "")
                    price = results.get("price", "Цена не указана")
                    rating = results.get("rating", {}).get("avg_rating", "Рейтинг отсутствует")
                    rating_count = results.get("rating", {}).get("rating_count", 0)

                    full_preview_url = urljoin(HOTEL_API_URL_RANDOM, relative_preview)

                    # Скачиваем изображение и сохраняем его как временный файл
                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    hotel_info = (
                        f"🌄 Тур: {title}\n"
                        f"💰 Цена: {price} сом\n"
                        f"⭐ Рейтинг: {rating} (Отзывов: {rating_count})"
                    )

                    await state.update_data(next_link=next_link)
                    await state.update_data(previous_link=previous_link)
                    with open(temp_image_path, 'rb') as photo_file:
                        await bot.send_photo(callback_query.message.chat.id, photo=photo_file, caption=hotel_info)

                    os.remove(temp_image_path)

                    # Обновляем инлайн-клавиатуру для следующей страницы
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    if hotels_data.get("previous"):
                        keyboard.add(InlineKeyboardButton("Предыдущий", callback_data="previous_page_activity"))
                    if hotels_data.get("next"):
                        keyboard.add(InlineKeyboardButton("Следующий", callback_data="next_page_activity"))

                    await bot.send_message(callback_query.message.chat.id, "Выберите действие:", reply_markup=keyboard)
                    # await callback_query.message.edit_reply_markup(reply_markup=keyboard)

                else:
                    await callback_query.message.answer("Извините, произошла ошибка при получении данных о турах.")
        except Exception as e:
            await callback_query.message.answer("Извините, произошла ошибка при получении данных о турах.")
            print(str(e))


# Обработчик выбора "🎲 Случайный тур"

@dispatcher.message_handler(lambda message: message.text == '🎲 Случайный тур', state=UserState.tour)
async def random_tour_command(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(TOUR_API_URL_RANDOM) as response:
                if response.status == 200:
                    hotel_data = await response.json()
                    title = hotel_data.get("title", "Название неизвестно")
                    relative_preview = hotel_data.get("preview", "")
                    price = hotel_data.get("price", "Цена не указана")
                    rating = hotel_data.get("rating", {}).get("rating__avg", "Рейтинг отсутствует")
                    rating_count = hotel_data.get("rating", {}).get("rating_count", 0)

                    full_preview_url = urljoin(TOUR_API_URL_RANDOM, relative_preview)

                    # Скачиваем изображение и сохраняем его как временный файл
                    async with session.get(full_preview_url) as image_response:
                        image_data = await image_response.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
                            temp_image.write(image_data)
                            temp_image_path = temp_image.name

                    hotel_info = (
                        f"🌄 Тур: {title}\n"
                        f"💰 Цена: {price} сом\n"
                        f"⭐ Рейтинг: {rating} (Отзывов: {rating_count})"
                    )

                    with open(temp_image_path, 'rb') as photo_file:
                        await message.answer_photo(photo=types.InputFile(photo_file), caption=hotel_info)

                    os.remove(temp_image_path)  # Удаляем временный файл
                else:
                    await message.answer("Извините, произошла ошибка при получении данных о туре.")
        except Exception as e:
            await message.answer("Извините, произошла ошибка при получении данных о туре.")
            print(str(e))  # Выводим ошибку для отладки

# Обработчик кнопки "⬅️ Назад"
@dispatcher.message_handler(lambda message: message.text == '⬅️ Назад', state='*')
async def back_to_main_menu(message: types.Message, state: FSMContext):
    # Отправляем главное меню
    await start_command(message, state)




# Handle all messages
@dispatcher.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


def main():
    from aiogram import executor
    executor.start_polling(dispatcher, skip_updates=True)


if __name__ == '__main__':
    main()
