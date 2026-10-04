import random
import telebot
from telebot import types,apihelper
from database import SessionLocal,User,Business,init_db
from config import TOKEN
from keyboards import get_action_keyboard,get_main_keyboard
from game_events import show_stats
from utils import check_balance,all_business_names,format_user
from bot_instance import refresh_user_info,go_back,bot
from game_events import show_stats,show_all,show_top
from handlers.start import create_users,start,help,balance,main_choose,send_message
from handlers.trade import buy,process_buy_step,sell,process_sell,work,upgrade,give_money


init_db()


bot.polling(non_stop=True)