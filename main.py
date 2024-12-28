import logging
import telebot
from dotenv import load_dotenv
import os
from libs import db
from libs import get_all

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Уровень логирования
    handlers=[
        logging.FileHandler("bot.log"),  # Логирование в файл
        logging.StreamHandler()  # Логирование в консоль
    ]
)

logger = logging.getLogger(__name__)

db_path = "storage/db.db"

# Загрузка переменных окружения
load_dotenv()
tg_token = os.getenv("telegram_token")
logger.info("Токен бота загружен.")

bot = telebot.TeleBot(tg_token)
logger.info("Бот загружен.")

@bot.message_handler(commands=["start", "Start"])
def start(message):
    logger.info(f"Команда /start от пользователя {message.from_user.id}.")
    check = db.get_data(db_path, "SELECT tg_id FROM main WHERE tg_id = ?", (message.from_user.id,))
    if check is None:
        logger.info(f"Пользователь {message.from_user.id} не существует, создаю запись.")
        db.execute_request(db_path, "INSERT INTO main (tg_id, city) VALUES (?, ?)", (message.from_user.id, "not_set"))
    else:
        logger.info(f"Пользователь {message.from_user.id} существует, ничего не трогаю.")
    bot.send_message(message.chat.id, "👋 Здравствуйте, я погодный бот! Я расскажу вам погоду в вашем городе прямо сейчас. ☀️")
    bot.send_message(message.chat.id, "Чтобы начать, поставьте свой город командой /set_city или, если вы уже настроили город, можете посмотреть погоду командой /weather.")

@bot.message_handler(commands=["help", "Help"])
def help_command(message):
    logger.info(f"Команда /help от пользователя {message.from_user.id}.")
    bot.send_message(message.chat.id, "🛠️ Команды:\n/start - вывести стартовое приветствие. 👋\n/set_city - Поставить свой город. 🌍\n/weather - Показать погоду в вашем городе. 🌦️\n/help - Вывести это сообщение. 📜")
@bot.message_handler(commands=["set_city"])
def set_city(message):
    logger.info(f"Команда /set_city от пользователя {message.from_user.id}.")
    check = db.get_data(db_path, "SELECT tg_id FROM main WHERE tg_id = ?", (message.from_user.id,))  
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("📍 Определить город.", request_location=True)
    keyboard.add(button)

    if check is None:
        bot.send_message(message.chat.id, "❗️ Вы ещё не ставили город, нажмите на кнопку снизу, чтобы определить ваш город.", reply_markup=keyboard)
    else:
        city_target = db.get_data(db_path, "SELECT city FROM main WHERE tg_id =?", (message.from_user.id,))
        if city_target != "not_set":
            bot.send_message(message.chat.id, f"🌆 У вас стоит город: {city_target}. Нажмите кнопку снизу, чтобы определить и поменять город.", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "❗️ Вы ещё не ставили город, нажмите на кнопку снизу, чтобы определить ваш город.", reply_markup=keyboard)

@bot.message_handler(content_types=["location"])
def city_update(message):
    try:
        lat = message.location.latitude
        lon = message.location.longitude
        city = get_all.get_city(lat, lon)
        bot.send_message(message.chat.id, f"🏙️ Установлен город: {city}", reply_markup=telebot.types.ReplyKeyboardRemove())
        logger.info(f"Юзер {message.from_user.id} сменил город на {city}.")
        db.execute_request(db_path, "UPDATE main SET city = ? WHERE tg_id = ?", (city, message.from_user.id,))
    except Exception as e:
        logger.error(f"Ошибка при обновлении города: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка при определении вашего города. Пожалуйста, попробуйте еще раз.")
@bot.message_handler(commands=["weather"])
def weather(message):
    try:
        deleteneg = bot.send_message(message.chat.id, "⏳ Запрашиваю погоду...")
        city_target = db.get_data(db_path, "SELECT city FROM main WHERE tg_id = ?", (message.from_user.id,))

        if city_target is None or city_target == "not_set":
            bot.send_message(message.chat.id, "🚫 Город не установлен. Пожалуйста, установите город с помощью команды /set_city.")
            return

        weather = get_all.get_weather(city_target)
        bot.send_message(message.chat.id, f"🌤️ Погода в городе {city_target}:")
        bot.send_message(
            message.chat.id,
            text=(
                f"🌡️ Температура: {weather[0]['temp']}°C\n"
                f"💨 Ощущается как: {weather[0]['feels_like']}°C\n"
                f"📉 Минимальная температура: {weather[0]['temp_min']}°C\n"
                f"📈 Максимальная температура: {weather[0]['temp_max']}°C\n"
                f"💧 Давление: {weather[0]['pressure']} мм рт. ст.\n"
                f"🌬️ Ветер: {weather[1]['speed']} м/с"
            )
        )
        bot.delete_message(message.chat.id, deleteneg.id)
    except Exception as e:
        logger.error(f"Ошибка при получении погоды: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка при получении погоды. Пожалуйста, попробуйте еще раз.")

@bot.message_handler(commands=["autor"])
def autor(message):
    logger.info(f"Команда /autor от пользователя {message.from_user.id}.")
    bot.send_message(message.chat.id, "👤 Меня создал: kos000113\nTelegram: @kos000113\nGithub: https://github.com/kostya2023/telegram_weather_bot\nDonation Alerts: https://www.donationalerts.com/r/kostyagot")

if __name__ == "__main__":
    logger.info("Запуск бота.")
    bot.infinity_polling()
