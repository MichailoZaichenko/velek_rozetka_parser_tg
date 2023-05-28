# Импортируем необходимые библиотеки
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import json # импортируем библиотеку для работы с JSON

# Задаем URL сайта и параметры поиска
url = "https://rozetka.com.ua/bicycles/c83884/"
params = {"search_text": "велосипед"}

# Отправляем запрос на сайт и получаем ответ
response = requests.get(url, params=params)

# Проверяем статус ответа
if response.status_code == 200:
    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.text, "html.parser")
    # Находим тег <script>, который содержит JSON-строку с данными о товарах
    script = soup.find("script", id="server-app-state")
    if script is not None:
        # Извлекаем текст из тега и удаляем лишние символы в начале и конце строки
        json_string = script.text.strip("window.__PRELOADED_STATE__ = ").strip(";")
        # Преобразуем JSON-строку в словарь Python с помощью библиотеки json
        data_dict = json.loads(json_string)
        # Находим ключ, который содержит список товаров
        products_key = "productsSearch:productsSearch:products"
        # Получаем список товаров из словаря по ключу
        products_list = data_dict[products_key]
    else:
        # Выводим сообщение об ошибке
        print("Не удалось найти тег <script> с данными о товарах")
    # Извлекаем текст из тега и удаляем лишние символы в начале и конце строки
    json_string = script.text.strip("window.__PRELOADED_STATE__ = ").strip(";")
    # Преобразуем JSON-строку в словарь Python с помощью библиотеки json
    data_dict = json.loads(json_string)
    # Находим ключ, который содержит список товаров
    products_key = "productsSearch:productsSearch:products"
    # Получаем список товаров из словаря по ключу
    products_list = data_dict[products_key]
    # Создаем пустой список для хранения данных о товарах
    data = []
    # Для каждого элемента из списка products_list
    for product in products_list:
        # Находим ссылку на фотографию товара
        image = product["images"][0]["big"]
        # Находим название товара
        title = product["title"]
        # Находим цену товара
        price = product["price"]
        # Добавляем данные о товаре в список data
        data.append({"image": image, "title": title, "price": price})

# Создаем объект бота с токеном
bot = telebot.TeleBot("6240094238:AAFog1fSFvYUi1qtiq0Rz7dQiinGgaCVr64")

# Функция для обработки команды /start
@bot.message_handler(commands=["start"])
def start(message):
    # Кнопка для перехода к товарам
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('🛒 Перейти к товарам')
    markup.add(button1)
    # Отправляем приветственное сообщение с прикрепленной к нему кнопкой
    bot.send_message(message.chat.id, 'Привет! Я бот, который может показать тебе велосипеды с сайта Rozetka.', reply_markup=markup)

# Функция для обработки сообщений с текстом "🛒 Перейти к товарам"
@bot.message_handler(func=lambda message: message.text == '🛒 Перейти к товарам')
def goodsChapter(message):
    # Отправляем сообщение с текстом "Вот все товары, которые сейчас находятся в продаже:"
    bot.send_message(message.chat.id, 'Вот все товары, которые сейчас находятся в продаже:')
    # Используем цикл for для отправки информации о каждом товаре из списка data
    for i in range(len(data)):
        # Получаем данные о товаре из списка data по номеру
        item = data[i]
        # Отправляем фотографию товара по ссылке из данных
        bot.send_photo(message.chat.id, item["image"])
        # Отправляем название и цену товара из данных
        bot.send_message(message.chat.id, f"🔹 Товар #{i+1}: {item['title']}\nЦена: {item['price']} грн.")
    # Кнопка для возврата в меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button5 = types.KeyboardButton('↩️ Назад в меню')
    markup.add(button5)
    # Отправляем сообщение с прикрепленной к нему кнопкой
    bot.send_message(message.chat.id, 'Чтобы вернуться в главное меню, нажмите на кнопку ниже.', reply_markup=markup)

# Функция для обработки сообщений с текстом "🔹 Товар #" (где # - номер от 1 до 4)
@bot.message_handler(func=lambda message: message.text.startswith('🔹 Товар'))
def showProduct(message):
    # Получаем номер товара из текста сообщения
    number = int(message.text.split('#')[1].split(':')[0]) - 1
    # Проверяем, что номер товара в допустимом диапазоне
    if 0 <= number < len(data):
        # Получаем данные о товаре из списка data по номеру
        item = data[number]
        # Отправляем фотографию товара по ссылке из данных
        bot.send_photo(message.chat.id, item["image"])
        # Отправляем название и цену товара из данных
        bot.send_message(message.chat.id, f"{item['title']}\nЦена: {item['price']} грн.")
    else:
        # Отправляем сообщение об ошибке
        bot.send_message(message.chat.id, "Такого товара нет в списке.")

# Функция для обработки сообщений с текстом "↩️ Назад в меню"
@bot.message_handler(func=lambda message: message.text == '↩️ Назад в меню')
def backToMenu(message):
    # Кнопка для перехода к товарам
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('🛒 Перейти к товарам')
    markup.add(button1)
    # Отправляем сообщение с прикрепленной к нему кнопкой
    bot.send_message(message.chat.id, 'Вы вернулись в главное меню.', reply_markup=markup)

# Запускаем бота
bot.polling()
