import random
import telebot
from telebot import types
from database import SessionLocal,User,Business,init_db
from bot_instance import bot
from utils import check_balance
from utils import format_user

random_events = [
    "🌤️ Хорошая погода — спрос увеличен!",
    "🌧️ Плохая погода — спрос снижен.",
    "💥 Горячая распродажа! Все цены снижены на 10%.",
    "🚨 Кража в магазине! Вы потеряли 5 единиц товара.",
    "🎉 Праздник в городе — вы получили +50 к прибыли!",
    "📉 Кризис — все товары дешевле на 15%",
    "📈 Подорожание — закупочные цены увеличились на 10%",
    '🏪 Открылся конкурент — ваша цена продажи снижена на 10%',
    '🎰 Джекпот - ваши деньги умножаются в два раза!'
]


@bot.message_handler(func=lambda message: message.text == 'Статистика')
def show_stats(message):
    user_id = message.chat.id
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, 'вы не вошли в систему')
            return
        
        biz = session.query(Business).all()
        event = random.choice(random_events)
        bot.send_message(message.chat.id,f'События дня: {event}')

        if "погода — спрос увеличен" in event:
            user.profit += 50
            user.money += 50
        elif "погода — спрос снижен" in event:
            user.profit -= 20
            user.money -= 20
        elif "Кража" in event:
            lost = min(5, user.inventory)
            user.inventory -= lost
        elif "Праздник" in event:
            user.money += 50
            user.profit += 50
        elif "Кризис" in event:
            user.profit -= 30
            user.money -= 30
        elif "Подорожание" in event:
            for key in biz:
                key.buy_price = int(key.buy_price * 1.1)
        elif 'Открылся конкурент' in event:
            if not user.selected_business:
                bot.send_message(message.chat.id, 'Выберите бизнес')
                return
            bus = user.selected_business
            biz = session.query(Business).filter_by(name=bus).first()
            if biz:
                biz.buy_price += int(biz.buy_price * 0.1)
                session.commit()
                bot.send_message(message.chat.id, f'Подорожание товара на 10 процентов: {biz.buy_price}')
        elif 'Джекпот' in event:
            user.money *= 2
            bot.send_message(message.chat.id,f'Джекпот. Ваши деньги умножились в два раза! {user.money}$')
            session.commit()

        stats_text = (
                f"💰 Баланс: {user.money}$\n"
                f"📦 Инвентарь: {user.inventory} шт.\n"
                f"📈 Прибыль: {user.profit}$\n"
                f"💼 Бизнес: {user.selected_business or 'Не выбран'}"
            )
        session.commit()
        bot.send_message(message.chat.id, f"{stats_text}\n{check_balance(user_id)}")
    finally:
        session.close()

@bot.message_handler(func=lambda message: message.text == 'Все игроки')
def show_all(message):
    session = SessionLocal()
    try:
        # Сортировка: по деньгам (богатые сверху)
        users = session.query(User).order_by(User.money.desc()).all()
    finally:
        session.close()

    if not users:
        bot.send_message(message.chat.id, 'Пока нет игроков 😢')
        return

    header = f"📋 <b>Список всех игроков</b> (всего: {len(users)})\n\n"

    # Telegram лимит ~4096 символов — режем на части
    chunks = []
    current = header
    for i, u in enumerate(users, start=1):
        block = format_user(u, i) + "\n\n"
        if len(current) + len(block) > 3800:
            chunks.append(current)
            current = ""
        current += block
    if current:
        chunks.append(current)

    for chunk in chunks:
        bot.send_message(message.chat.id, chunk, parse_mode="HTML")

@bot.message_handler(func= lambda message: message.text == 'Топ игроков')
def show_top(message):
    session = SessionLocal()
    try:
        users = session.query(User).order_by(User.money.desc()).limit(10).all()
    finally:
        session.close()

    if not users:
        bot.send_message(message.chat.id,'Пока что нет игроков')   
        return
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    lines = ["🏆 <b>Топ-10 игроков</b>\n"]
    for i, u in enumerate(users):
        name = u.first_name or (f"@{u.username}" if u.username else f"id{u.user_id}")
        lines.append(f"{medals[i]} {name} — {int(u.money)}$ (id: {u.user_id})")

    bot.send_message(message.chat.id, "\n".join(lines), parse_mode="HTML")

