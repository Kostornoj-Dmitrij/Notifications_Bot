import telebot
from telebot import types
from main import bot, user_balance, user_data
from database import cursor, conn
from config import KEYWORDS_LIST
import kb
def show_profile(user_id):
    balance = user_balance[user_id]
    keyboard = kb.profile_keyboard
    bot.send_message(user_id, f"Ваш баланс: {balance} руб", reply_markup=keyboard)


def show_payment_options(user_id):
    keyboard = kb.payment_keyboard
    bot.send_message(user_id, "Выберите сумму для пополнения:", reply_markup=keyboard)


def show_subscribe_options(user_id):
    keyboard = kb.subscribe_keyboard
    bot.send_message(user_id, "Выберите вариант подписки:", reply_markup=keyboard)


def show_support_options(user_id):
    keyboard = kb.support_keyboard

    bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)


def show_bot_info(user_id):
    keyboard = kb.profile_back_keyboard
    bot.send_message(user_id, "Это бот для уведомлений...", reply_markup=keyboard)


def show_statistics(user_id):
    keyboard = kb.profile_back_keyboard
    bot.send_message(user_id, "Статистика...", reply_markup=keyboard)


def show_chats_info(user_id):
    cursor.execute('SELECT COUNT(chat_id) FROM Chats WHERE t_user_chat_id = ?', (user_id))
    user_data[user_id].chat_id = cursor.fetchone()[0]
    keyboard = kb.all_chats_info_keyboard
    bot.send_message(user_id, f"Включенных в мониторинг чатов - {user_data[user_id].chat_id}", reply_markup=keyboard)

def find_message(message, user_id):
    message_text = message.text.lower()
    message_link = f"https://t.me/{message.chat.username}/{message.message_id}"
    chat_name = message.chat.title
    message_first_text = ' '.join(message_text.split()[:5])
    flag = False
    for keyword in KEYWORDS_LIST:
        if keyword in message_text:
            flag = True
    if flag:
        bot.send_message(user_id, f'"{chat_name}" пишет: "{message_first_text}..."\nСсылка на полное сообщение: {message_link}')
        cursor.execute('INSERT INTO FindMessages (t_message_link, keywords_id, chat_id, user_id, sender, first_text) VALUES (?, ?, ?, ?, ?, ?)', (message_link, user_data[user_id].keywords_id, user_data[user_id].chat_id, user_data[user_id].user_id, chat_name, message_first_text))
        conn.commit()