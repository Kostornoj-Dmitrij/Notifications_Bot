import telebot
from telebot import types
import pyodbc
import config
from config import TOKEN, YOOTOKEN, KEYWORDS_LIST

bot = telebot.TeleBot(TOKEN)
user_balance = {'user_id': 0}
user_data = {}