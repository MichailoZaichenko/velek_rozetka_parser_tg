# Импортируем необходимые библиотеки
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import random
file = open('./mytoken.txt')
mytoken = file.read()
# Передаем сюда токен, который получили от FatherBot
bot = telebot.TeleBot(mytoken)

options = Options()
options.add_argument('--headless')  # Run in headless mode (without opening a browser window)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get('https://www.google.com/')

data = []

# Задаем URL сайта и параметры поиска
url = 'https://rozetka.com.ua/bicycles/c83884/page={page}/'
params = {"search_text": "велосипед"}
for page in range(1, 11):
    try:
        # Load the page using Selenium WebDriver
        driver.get(url.format(page=page, **params))

        # Extract the page content after it has been rendered
        page_content = driver.page_source

        # Create BeautifulSoup object for parsing
        soup = BeautifulSoup(page_content, 'html.parser')

        # Scraping logic goes here...
        products = soup.find_all("div", class_="goods-tile__inner")
        # Создаем пустой список для хранения данных о товарах
        if products:
            for product in products:
                # Находим ссылку на фотографию товара
                image = product.find("img", class_="lazy_img_hover").get("src")
                # Находим название товара
                title = product.find("span", class_="goods-tile__title").text
                # Находим цену товара
                price = product.find("span", class_="goods-tile__price-value").text
                # Добавляем данные о товаре в список data
                data.append({"image": image, "title": title, "price": price})
                time.sleep(random(1, 6))
        else:
            print('net')

    except Exception as e:
        print('Error occurred:', e)

# Clean up the WebDriver instance
driver.quit()

# Функция для обработки команды /start
@bot.message_handler(commands=["start"])
def start(message):
    # Кнопка для перехода к товарам
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('🛒 Перейти к товарам')
    markup.add(button1)
    # Отправляем приветственное сообщение с прикрепленной к нему кнопкой
    bot.send_message(message.chat.id, 'Привет! Я бот, который может показать тебе велосипеды с сайта Rozetka.', reply_markup=markup)

@bot.message_handler(content_types='photo')
def get_photo(message):
    bot.send_message(message.chat.id, 'У меня нет возможности просматривать фото :(')

# Функция для обработки сообщений с текстом "🛒 Перейти к товарам"
@bot.message_handler(func=lambda message: message.text == '🛒 Перейти к товарам')
def goodsChapter(message):
    # Кнопки для товаров
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Використовуємо цикл for для створення кнопок динамічно
    for i in range(0, len(data)):
        button = types.KeyboardButton(f"🔹 Товар #{i+1}: {data[i]['title']}")
    # Додаємо кнопку в розмiтку клавiатури
        markup.add(button)
    button5 = types.KeyboardButton('↩️ Назад в меню')
    markup.add(button5)
    # Отправляем сообщение с прикрепленными к нему кнопками товаров
    bot.send_message(message.chat.id, 'Вот все товары, которые сейчас находятся в продаже:', reply_markup=markup)
    for i in range(len(data)):
        # Получаем данные о товаре из списка data по номеру
        item = data[i]
        # Отправляем фотографию товара по ссылке из данных
        bot.send_photo(message.chat.id, item["image"])
        # Отправляем название и цену товара из данных
        bot.send_message(message.chat.id, f"🔹 Товар #{i + 1}: {item['title']}\nЦена: {item['price']} грн.")

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
