import random
from bot_instance import bot
from database import SessionLocal, User, Business
from utils import check_balance
from game_events import show_stats


@bot.message_handler(func=lambda message: message.text == 'Купить товар')
def buy(message):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, 'вы не вошли в систему')
            return
        if not user.selected_business:
            bot.send_message(message.chat.id, 'Выберите тип бизнеса!')
            return

        biz = session.query(Business).filter_by(name=user.selected_business).first()
        product_name = biz.product
        price = biz.buy_price
        business_name = biz.name
    finally:
        session.close()

    bot.clear_step_handler_by_chat_id(message.chat.id)
    msg = bot.send_message(message.chat.id, f'Сколько {product_name} вы хотите купить? Цена за штуку: {price}')
    bot.register_next_step_handler(msg, process_buy_step, business_name)

def process_buy_step(message, business_name):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, 'вы не вошли в систему')
            return

        biz = session.query(Business).filter_by(name=business_name).first()

        try:
            quantity = int(message.text)
            price = biz.buy_price
            total = quantity * price

            if quantity + user.inventory > user.max_items:
                bot.send_message(message.chat.id, f'На складе недостаточно мест. Максимум {user.max_items}!')
                return
            if user.money < total:
                bot.send_message(message.chat.id, "Не достаточно денег")
                return

            user.money -= total
            user.inventory += quantity
            user.profit -= total
            session.commit()
            bot.send_message(message.chat.id, f'Вы купили {quantity} штук {biz.product} за {total} денег')
        except:
            bot.send_message(message.chat.id, 'Введите корректное число!')
    finally:
        session.close()

    show_stats(message)

@bot.message_handler(func=lambda message: message.text == 'Продать товар')
def sell(message):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, 'вы не вошли в систему')
            return
        if not user.selected_business:
            bot.send_message(message.chat.id, 'Выберите тип бизнеса!')
            return
    
        biz = session.query(Business).filter_by(name=user.selected_business).first()
        product_name = biz.product
        price = biz.sell_price
        business_name = biz.name
        session.commit()
    finally:
        session.close()
    
    bot.clear_step_handler_by_chat_id(message.chat.id)
    msg = bot.send_message(message.chat.id, f'Сколько {product_name} вы хотите Продать? Цена за штуку: {price}')
    bot.register_next_step_handler(msg, process_sell, business_name)



def process_sell(message,business_name):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, 'вы не вошли в систему')
            return
    
        biz = session.query(Business).filter_by(name=business_name).first()
    
        try:
            quantity = int(message.text)
            price = biz.sell_price
            total = quantity * price
            if quantity > user.inventory:
                bot.send_message(message.chat.id,'Количество не соответвует!')
                quantity = user.inventory
    
            user.money += total
            user.inventory -= quantity
            user.profit += total
            session.commit()
            bot.send_message(message.chat.id, f'Вы Продали {quantity} штук {biz.product} за {total} денег')
        except:
            bot.send_message(message.chat.id, 'Введите корректное число!')
    finally:
        session.close()
    
    show_stats(message)

@bot.message_handler(func=lambda message: message.text == "Работа")
def work(message):
    earnings = random.randint(50, 150)
    
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, 'вы не вошли в систему')
            return
    
        user.money += earnings
        session.commit()
        bot.send_message(message.chat.id, f"Вы поработали и заработали {earnings}$!")
    finally:
        session.close()

#=====================Улучшения====
@bot.message_handler(func=lambda message:message.text == 'Улучшить')
def upgrade(message):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, 'вы не вошли в систему')
            return
        if not user.selected_business:
            bot.send_message(message.chat.id,'вы не выброли бизнес')
            return
        
        bus = user.selected_business
        biz = session.query(Business).filter_by(name=bus).first()
        
        if user.money < 500:
            bot.send_message(message.chat.id,'У вас нету 500 доллров! АХАХАХАХХААХЪАХАХАХАХАХА')
            return
        
        user.money -= 500
        biz.sell_price += int(biz.sell_price * 0.1)
        user.max_items += 50
        session.commit()
        bot.send_message(message.chat.id,f'Вы успешно улучшили бизнес. Теперь цена продажи: {biz.sell_price}, И макс вещей увеличен на 50!\n{check_balance(user_id)}')
    finally:
        session.close()

def give_money_func(message,another_user_id,money):
    session = SessionLocal()
    user_id = message.chat.id
    try:
        if user_id == another_user_id:
            bot.send_message(message.chat.id,'Нельзя передовать себе деньги')
            return
        
        user = session.query(User).filter_by(user_id=user_id).first()
        another_user = session.query(User).filter_by(user_id=another_user_id).with_for_update().first()
        
        if not user:
            bot.send_message(message.chat.id, 'вы не вошли в систему')
            return
        if user.money < money:
            bot.send_message(message.chat.id,f'У вас недостаточно денег для перевода!')
            return
        if not another_user:
            bot.send_message(user_id, 'Игрок с таким ID не найден')
            return
        
        user.money -= money
        user.profit -= money
        another_user.money += money
        another_user.profit += money 
        bot.send_message(message.chat.id,f'Вы успешно перевели деньги {another_user.username} на сумму: {money}')
        session.commit()
        try:
            bot.send_message(another_user.user_id,f'Вам перевел {money} от {user.username}')
        except Exception as notify_error:
            print(f'Не удалось уведомить получателя: {notify_error}')
    except Exception as e:
        session.rollback()
        print(f'Ошибка перевода: {e}')
        bot.send_message(user_id, 'Произошла ошибка при переводе, попробуйте позже')
    finally:
        session.close()

@bot.message_handler(func=lambda message: message.text == 'Перевести деньги')
def give_money(message):
    msg = bot.send_message(message.chat.id, 'Введите ID игрока, которому хотите перевести деньги:')
    bot.register_next_step_handler(msg, get_receiver_id)


def get_receiver_id(message):
    if not message.text or not message.text.isdigit():
        msg = bot.send_message(message.chat.id, 'ID должен быть числом. Попробуйте ещё раз:')
        bot.register_next_step_handler(msg, get_receiver_id)
        return

    another_user_id = int(message.text)
    msg = bot.send_message(message.chat.id, 'Введите сумму перевода:')
    bot.register_next_step_handler(msg, get_amount, another_user_id)


def get_amount(message, another_user_id):
    if not message.text or not message.text.isdigit():
        msg = bot.send_message(message.chat.id, 'Сумма должна быть целым числом. Попробуйте ещё раз:')
        bot.register_next_step_handler(msg, get_amount, another_user_id)
        return

    money = int(message.text)
    give_money_func(message, another_user_id, money)
    return
