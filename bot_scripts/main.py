import telebot
from config import TOKEN, YOOTOKEN

bot = telebot.TeleBot(TOKEN)
user_balance = {'user_id': 0}
user_data = {}