import telebot
from telebot import types
from database import SessionLocal,User,Business,init_db

def check_balance(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if user and user.money <= 0:
            return 'Вы банкрот!'
    finally:
        session.close()

def all_business_names():
    session = SessionLocal()
    try:
        return [b.name for b in session.query(Business).all()]
    finally:
        session.close()

def format_user(u, index=None):
    """Красиво форматирует одного игрока."""
    # Имя: приоритет first_name → @username → id
    if u.first_name:
        name = u.first_name
    elif u.username:
        name = f"@{u.username}"
    else:
        name = "Без имени"

    uname = f"@{u.username}" if u.username else "—"
    biz = u.selected_business or "не выбран"

    prefix = f"{index}. " if index else ""
    return (
        f"{prefix}👤 <b>{name}</b> ({uname})\n"
        f"   🆔 <code>{u.user_id}</code>\n"
        f"   💼 {biz}\n"
        f"   💰 {u.money}$ | 📈 {u.profit}$ | 📦 {u.inventory} шт."
    )







