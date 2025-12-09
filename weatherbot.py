import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyowm import OWM
from pyowm.utils.config import get_default_config
import os
# ---------- НАСТРОЙКИ ----------
OWM_KEY = "9fe99b35774c29ad2a4ba10936262718"
BOT_TOKEN = "8487689537:AAF2WNMlPL9m0U0rw5iPQ-S3sqBe2yMOnXw"
CITY = "Калининград"

# ---------- PYOWM ----------
config = get_default_config()
config['language'] = 'ru'

owm = OWM(OWM_KEY, config)
mgr = owm.weather_manager()

# ---------- TELEGRAM ----------
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("Показать погоду", callback_data="get_weather")
    markup.add(btn)
    bot.send_message(message.chat.id, "Привет! Нажми кнопку, чтобы узнать погоду:", reply_markup=markup)

# Обработчик нажатия кнопки

@bot.callback_query_handler(func=lambda call: call.data == "get_weather")
def send_weather(call):
    observation = mgr.weather_at_place(CITY)
    w = observation.weather

    status = w.detailed_status
    feels = w.temperature('celsius')['feels_like']

    answ = (
        f"Мой совёнок ❤️\n"
        f"Сейчас в городе {CITY} — *{status}*.\n"
        f"Ощущается как: *{feels}°C*.\n"
        f"Одевайся теплее, пожалуйста 😘"
    )

    bot.send_message(call.message.chat.id, answ, parse_mode="Markdown")
bot.polling(non_stop=True)


