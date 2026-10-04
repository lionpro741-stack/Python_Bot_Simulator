import telebot
from telebot import types

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_cafe = types.KeyboardButton("Кафе")
    btn_shop = types.KeyboardButton('Магазин одежды')
    btn_online = types.KeyboardButton('Интернет магазин')
    btn_car = types.KeyboardButton('Автомойка')
    markup.add(btn_cafe,btn_shop,btn_online,btn_car)
    return markup

def get_action_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_buy = types.KeyboardButton("Купить товар")
    btn_sell = types.KeyboardButton('Продать товар')
    btn_stats = types.KeyboardButton("Статистика")
    btn_work = types.KeyboardButton('Работа')
    btn_upgrade = types.KeyboardButton('Улучшить')
    btn_all = types.KeyboardButton('Все игроки')
    btn_top = types.KeyboardButton('Топ игроков')
    btn_give_money = types.KeyboardButton('Перевести деньги')
    btn_back = types.KeyboardButton('Назад')
    markup.add(btn_buy,btn_sell,btn_stats,btn_work,btn_upgrade,btn_top,btn_all,btn_give_money,btn_back)
    return markup