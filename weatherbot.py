import os
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyowm import OWM
from pyowm.utils.config import get_default_config

# ---------- НАСТРОЙКИ ----------
OWM_KEY = os.environ.get("OWM_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CITY = os.environ.get("CITY", "Калининград")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")  # Сюда Render сам подставит URL

# ---------- PYOWM ----------
config = get_default_config()
config['language'] = 'ru'
owm = OWM(OWM_KEY, config)
mgr = owm.weather_manager()

# ---------- TELEGRAM ----------
bot = telebot.TeleBot(BOT_TOKEN)


def weather_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="☀️ Показать погоду",
            callback_data="weather"
        )
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Нажми кнопку, чтобы узнать погоду 💛",
        reply_markup=weather_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "weather")
def send_weather(call):
    try:
        bot.answer_callback_query(call.id)
        observation = mgr.weather_at_place(CITY)
        w = observation.weather

        status = w.detailed_status
        if status == 'ясно':
            st = f'{status} ☀️'
        elif status == 'пасмурно': 
            st = f'{status} 🌥️' 
        else:
            st = status
        feels = w.temperature('celsius')['feels_like']
        wind = w.wind()['speed']
        if wind < 5.0:
            com = 'Слабый ветер' 
        elif 5.0 <= wind < 10.0:
            com = 'Ветрено💨' 
        else:
            com = 'Сильный ветер'
        
        

        answ = (
            f"Мой совёнок ❤️\n"
            f"Сейчас — *{st}*.\n"            
            f"Ощущается как: *{round(feels,1)}°C*.\n"
            f"{com} \n\n"
            f"Одевайся теплее, любимая 😘"
        )
        
        bot.edit_message_text(
            answ,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=weather_keyboard()
        )
        
        
    except Exception as e:
        bot.send_message(call.chat.id, "Ошибка получения погоды 😢")
        print("Weather error:", e)

# ---------- FLASK ----------
app = Flask(__name__)

@app.route("/" + BOT_TOKEN, methods=['POST'])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/set_webhook")
def set_webhook():
    full_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=full_url)
    return f"Webhook set: {full_url}", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

