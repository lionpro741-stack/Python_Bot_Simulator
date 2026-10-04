from bot_instance import bot
from database import SessionLocal, User, Business
from keyboards import get_main_keyboard, get_action_keyboard
from utils import all_business_names

def create_users(user_id):
    session = SessionLocal()    
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id)
            session.add(user)
            session.commit()
    finally:
        session.close()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            session.add(User(user_id=user_id,username=username,first_name=first_name))
            session.commit()
        user.username = username
        user.first_name = first_name
        session.commit()
    except:
        bot.send_message(message.chat.id,'Возникла ошибка')
    finally:
        session.close()

    bot.send_message(message.chat.id, 'Добро пожаловать в бизнес симулятор!\n Выберите тип бизнеса:', reply_markup=get_main_keyboard())

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,'Данная игра зависет от ваших решений, в выборе бизнеса и закупа товара! покупай и продовай\n/start - начать играть\n/help - помощь\n/balance - посмотреть баланс денег')

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            session.add(User(user_id=user_id))
            session.commit()
            money = 1000
        else:
            money = user.money
    finally:
        session.close()

    bot.send_message(message.chat.id, f"Ваш баланс: {money}")


@bot.message_handler(func=lambda message: message.text in all_business_names())
def main_choose(message):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id)
            session.add(user)
        user.selected_business = message.text
        session.commit()
    finally:
        session.close()

    bot.send_message(message.chat.id, f'Вы выбрали: {message.text}!')
    bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup=get_action_keyboard())
   


def func_send_message(message,another_user_id,conntent):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        if user_id == another_user_id:
            bot.send_message(message.chat.id,'Зачем вам отпровлять себе же сообщение!')
            return
        
        user = session.query(User).filter_by(user_id=user_id).first()
        another_user = session.query(User).filter_by(user_id=another_user_id).first()
        if not user:
            bot.send_message(message.chat.id, 'Вы не вошли в систему')
            return
        if not another_user:
            bot.send_message(message.chat.id, 'Такого йди не существует!')
            return

        bot.send_message(message.chat.id,'Сообщение успешно отправлено!')
        try:
            bot.send_message(another_user.user_id,f'Вам пришло сообщение от {user.username}:\n{conntent}')
        except Exception as notify_error:
            print(f'Не удалось уведомить получателя: {notify_error}')    
    except Exception as e:
        session.rollback()
        print(f'Ошибка перевода: {e}')
        bot.send_message(user_id, 'Произошла ошибка при переводе, попробуйте позже')
    finally:
        session.close()

@bot.message_handler(commands=['chat'])
def send_message(message):
    msg = bot.send_message(message.chat.id,'Введите ID другого игрока:')
    bot.register_next_step_handler(msg,get_receiver_id)

def get_receiver_id(message):
    if not message.text:
        msg = bot.send_message(message.chat.id, 'ID должен быть числом. Попробуйте ещё раз:')
        bot.register_next_step_handler(msg, get_receiver_id)
        return

    another_user_id = int(message.text)
    msg = bot.send_message(message.chat.id, 'Введите текст для отправления:')
    bot.register_next_step_handler(msg, send_msg, another_user_id)   

def send_msg(message,another_user_id):
    if not message.text:
        msg = bot.send_message(message.chat.id, 'ID должен быть числом. Попробуйте ещё раз:')
        bot.register_next_step_handler(msg, get_receiver_id)
        return

    text = message.text
    func_send_message(message,another_user_id,text)
    return
    