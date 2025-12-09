import os
from flask import Flask, request
import telebot
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

@bot.message_handler(content_types=['text'])
def send_weather(message):
    try:
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
            
            f"Ощущается как: *{feels}°C*.\n"
            f"• ветер {com} \n\n"
            f"Одевайся теплее, любимая 😘"
        )

        bot.send_message(message.chat.id, answ)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка получения погоды 😢")
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

