import telebot
from telebot import apihelper
from config import TOKEN
from database import SessionLocal,User,Business,init_db
from keyboards import get_main_keyboard


apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN)

@bot.middleware_handler(update_types=['message'])
def refresh_user_info(bot_instance, message):
    if not message.from_user:
        return
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.username = message.from_user.username
            user.first_name = message.from_user.first_name
            session.commit()
    finally:
        session.close()


# --- Назад ---
@bot.message_handler(func=lambda message: message.text == "Назад")
def go_back(message):
    bot.send_message(message.chat.id, "Выберите тип бизнеса:", reply_markup=get_main_keyboard())

