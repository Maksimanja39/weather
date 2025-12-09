import os
import threading
from flask import Flask
import telebot
from pyowm import OWM
from pyowm.utils.config import get_default_config

# ---------- НАСТРОЙКИ ----------
OWM_KEY = "9fe99b35774c29ad2a4ba10936262718"
BOT_TOKEN = "8487689537:AAGXB1HEN0gVXdBS2Sopo5k7o-_jtpYrILA"
CITY = "Калининград"

# ---------- PYOWM ----------
config = get_default_config()
config['language'] = 'ru'

owm = OWM(OWM_KEY, config)
mgr = owm.weather_manager()

# ---------- TELEGRAM ----------
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['text'])
def send_weather(message):
    observation = mgr.weather_at_place(CITY)
    w = observation.weather

    status = w.detailed_status
    feels = w.temperature('celsius')['feels_like']
    wind=w.wind()
    if wind['speed']<5.0:
        com=str('Слабый ветер')
    elif wind['speed']>5.0 and wind['speed']<10.0:
        com=str('Ветрено')
    elif wind['speed']>10.0:
        com=str('Сильный ветер')

    answ = (
        f"Мой совёнок ❤️\n"
        f"Сейчас — *{status}*.\n"
        f"Ощущается как: *{feels}°C*.\n"
        f"{com}"
        f"Одевайся теплее, пожалуйста 😘"
    )

    bot.send_message(message.chat.id, answ, parse_mode="Markdown")

# ---------- ФУНКЦИЯ ЗАПУСКА БОТА ----------
def start_bot():
    bot.infinity_polling(skip_pending=True)

# ---------- FLASK ДЛЯ PORT ----------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    threading.Thread(target=start_bot).start()

    # Запуск веб-сервера (Render требует открыт порт)
    port = int(os.environ.get("PORT", 2500))
    app.run(host="0.0.0.0", port=port)


