from aiogram import Bot, Dispatcher
from config import TOKEN
bot = Bot(token = TOKEN)
dp = Dispatcher(bot)
user_balance = {'user_id': 0}
user_data = {}