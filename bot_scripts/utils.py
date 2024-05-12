import telebot
from telebot import types
from main import bot, user_balance, user_data
from database import cursor, conn
from config import KEYWORDS_LIST

def show_profile(user_id):
    balance = user_balance[user_id]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('О боте', callback_data='info'))
    keyboard.add(types.InlineKeyboardButton('Статистика', callback_data='stat'))
    keyboard.add(types.InlineKeyboardButton('Поддержка', callback_data='support'))
    keyboard.add(types.InlineKeyboardButton('Список чатов', callback_data='chats'))
    keyboard.add(types.InlineKeyboardButton('Пополнение баланса', callback_data='pay'))
    keyboard.add(types.InlineKeyboardButton('Оформить подписку', callback_data='subscribe'))
    bot.send_message(user_id, f"Ваш баланс: {balance} руб", reply_markup=keyboard)


def show_payment_options(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton('100 руб', callback_data='100'),
                 types.InlineKeyboardButton('300 руб', callback_data='300'),
                 types.InlineKeyboardButton('500 руб', callback_data='500'))
    keyboard.row(types.InlineKeyboardButton('1000 руб', callback_data='1000'),
                 types.InlineKeyboardButton('1500 руб', callback_data='1500'),
                 types.InlineKeyboardButton('2000 руб', callback_data='2000'))
    keyboard.row(types.InlineKeyboardButton('Отмена', callback_data='profile'))
    bot.send_message(user_id, "Выберите сумму для пополнения:", reply_markup=keyboard)


def show_subscribe_options(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton('Фрилансер, 5 чатов, 100 руб/мес', callback_data='sub_100'))
    keyboard.row(types.InlineKeyboardButton('Стандарт, 15 чатов, 300 руб/мес', callback_data='sub_300'))
    keyboard.row(types.InlineKeyboardButton('Стартап, 25 чатов, 450 руб/мес', callback_data='sub_450'))
    keyboard.row(types.InlineKeyboardButton('Компания, 50 чатов, 750 руб/мес', callback_data='sub_750'))
    keyboard.row(types.InlineKeyboardButton('Бесплатный месяц', callback_data='sub_0'))
    keyboard.row(types.InlineKeyboardButton('Тарифы на 3мес / 6 мес', callback_data='other_subscribe'))
    keyboard.row(types.InlineKeyboardButton('Отмена', callback_data='profile'))
    bot.send_message(user_id, "Выберите вариант подписки:", reply_markup=keyboard)


def show_support_options(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Написать в поддержку', url='https://www.google.com'))
    keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))

    bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)


def show_bot_info(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
    bot.send_message(user_id, "Это бот для уведомлений...", reply_markup=keyboard)


def show_statistics(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
    bot.send_message(user_id, "Статистика...", reply_markup=keyboard)


def show_chats_info(user_id):
    cursor.execute('SELECT COUNT(chat_id) FROM Chats WHERE t_user_chat_id = ?', (user_id))
    user_data[user_id].chat_id = cursor.fetchone()[0]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton('Список чатов', callback_data='chatsList'),
                 types.InlineKeyboardButton('Добавить чат', callback_data='addChat'),
                 types.InlineKeyboardButton('Удалить чат', callback_data='chatDeleteChoice'))
    keyboard.row(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
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