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

    answ = (
        f"Мой совёнок ❤️\n"
        f"Сейчас в городе {CITY} — *{status}*.\n"
        f"Ощущается как: *{feels}°C*.\n"
        f"Одевайся теплее, пожалуйста 😘"
    )

    bot.send_message(message.chat.id, answ, parse_mode="Markdown")

bot.polling(non_stop=True)
