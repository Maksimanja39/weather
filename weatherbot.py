import os
from flask import Flask, request
import telebot
from pyowm import OWM
from pyowm.utils.config import get_default_config

# ---------- НАСТРОЙКИ ----------
OWM_KEY = "9fe99b35774c29ad2a4ba10936262718"
BOT_TOKEN = "8487689537:AAGXB1HEN0gVXdBS2Sopo5k7o-_jtpYrILA"
CITY = "Калининград"

# Render даёт URL вида https://<app>.onrender.com
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://weather-3l92.onrender.com")  

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
            st = status + '☀️'
        elif status == 'пасмурно':
            st = status + '🌥️'
        else:
            st = status

        feels = w.temperature('celsius')['feels_like']
        wind = w.wind()
        speed = wind['speed']

        if speed < 5.0:
            com = 'Слабый ветер'
        elif 5.0 <= speed < 10.0:
            com = 'Ветрено💨'
        else:
            com = 'Сильный ветер'

        answ = (
            f"Мой совёнок ❤️\n"
            f"Сейчас — *{st}* \n"
            f"Ощущается как: *{feels}°C* \n"
            f"{com} \n"
            f"Одевайся теплее, пожалуйста 😘"
        )
        bot.send_message(message.chat.id, answ, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "Не удалось получить погоду. Попробуй позже.")
        print(f"Ошибка погоды: {e}")

# ---------- FLASK ----------
app = Flask(__name__)

# Telegram будет слать обновления сюда
@app.route('/' + BOT_TOKEN, methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Invalid content-type', 403

@app.route("/")
def home():
    return "Weather bot is running! ✅"

# Устанавливаем webhook при запуске
@app.route("/set_webhook")
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    result = bot.set_webhook(url=webhook_url)
    return f"Webhook set to {webhook_url}: {result}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 2500))
    app.run(host="0.0.0.0", port=port)
