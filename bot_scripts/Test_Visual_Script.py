import telebot
import pyodbc
from telebot import types
import requests
from telebot import join_chat

class User:
    def __init__(self, user_id):
        self.state = 'chat_start'
        self.chat_name = ''
        self.chat_link = ''
        self.keywords = ''
        self.user_id = user_id

TOKEN = '6534454602:AAH7IlOdqFzRtXAZ2wffIOFpHYFTWdb7-1A'
YOOTOKEN = '381764678:TEST:83858'

bot = telebot.TeleBot(TOKEN)
user_balance = {'user_id': 0}
user_data = {}

file_path = ''
cost = 0.2
current_message_number = 1
output_format = None
images_folder = 'D:/Scanner/images'

conn = pyodbc.connect(
    'driver={ODBC Driver 18 for SQL Server};'
    'Server=DESKTOP-BIV7UD0\SQLEXPRESS01;'
    'Database=notifications;'
    'Trusted_Connection=yes;'
    'Encrypt=optional;'
)


cursor = conn.cursor()




@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    username = message.chat.username
    cursor.execute('''SELECT * FROM Users WHERE username=?''', username)
    result = cursor.fetchone()
    user = User(user_id)
    user_data[user_id] = user
    if not result:
        user_balance[user_id] = float(1000)
        cursor.execute('''INSERT INTO Users (username, t_user_chat_id, balance) VALUES (?, ?, ?)''', username, user_id, user_balance[user_id])
        conn.commit()
    else:
        user_balance[user_id] = result[3]

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'),
                 types.InlineKeyboardButton('Мониторинг чатов', callback_data='chatsList'))

    bot.send_message(user_id, "Привет! Добро пожаловать в бота.", reply_markup=keyboard)

@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'add_chat') 
def add_chat_handler(message): 
    user_data[message.chat.id].chat_name = message.text 
    user_data[message.chat.id].state = 'add_link'
    bot.send_message(message.chat.id, "Теперь введите ссылку на чат.")

@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'add_link') 
def add_link_handler(message): 
    # Добавить ссылку в список чатов пользователя 
    user_data[message.chat.id].chat_link = message.text
    bot.join_chat(user_data[message.chat.id].chat_link)
    try:
        
        bot.send_message(message.chat.id, f'Бот успешно присоединился к группе {user_data[message.chat.id].chat_link}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Не удалось присоединить бота к группе: {e}')
    
    user_data[message.chat.id].state = 'add_keywords'
    
    bot.send_message(message.chat.id, "Теперь введите ключевые слова или фразы через запятую.")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    if message.text == '/profile':
        show_profile(user_id)
    elif message.text == '/pay':
        show_payment_options(user_id)
    elif message.text == '/subscribe':
        show_subscribe_options(user_id)
    elif message.text == '/support':
        show_support_options(user_id)
    elif message.text == '/info':
        show_bot_info(user_id)
    elif message.text == '/stat':
        show_statistics(user_id)
    elif message.text == '/chats':
        show_chats_info(user_id)
    elif message.text == '/test':
        bot.send_message(user_id, '"Эмпатия машины" пишет: "xAI опубликовала исходный код модели..."\nСсылка на полное сообщение: https://t.me/c/1948713469/106')
    else:
        bot.send_message(user_id, "Извините, не могу обработать этот запрос.")


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

    bot.send_message(user_id, "Выберите сумму для пополнения:", reply_markup=keyboard)


def show_subscribe_options(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton('Фрилансер, 5 чатов, 100 руб/мес', callback_data='sub_100'))
    keyboard.row(types.InlineKeyboardButton('Стандарт, 15 чатов, 300 руб/мес', callback_data='sub_300'))
    keyboard.row(types.InlineKeyboardButton('Стартап, 25 чатов, 450 руб/мес', callback_data='sub_450'))
    keyboard.row(types.InlineKeyboardButton('Компания, 50 чатов, 750 руб/мес', callback_data='sub_750'))
    keyboard.row(types.InlineKeyboardButton('Бесплатный месяц', callback_data='sub_0'))
    keyboard.row(types.InlineKeyboardButton('Тарифы на 3мес / 6 мес', callback_data='other_subscribe'))

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
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton('Список чатов', callback_data='chatsList'),
                 types.InlineKeyboardButton('Добавить чат', callback_data='addChat'),
                 types.InlineKeyboardButton('Удалить чат', callback_data='deleteChat'))
    bot.send_message(user_id, "Включенных в мониторинг чатов - ...", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    
    if call.data in ['100', '300', '500', '1000', '1500', '2000']:
        prices = [types.LabeledPrice(label='Руб', amount = int(call.data)*100)]

        bot.send_invoice(call.message.chat.id, title='Пополнение баланса',
                         description='payment', invoice_payload='pay_add',
                         provider_token=YOOTOKEN, currency='RUB',
                         start_parameter='test_bot', prices=prices)
        
    elif call.data in ['sub_100', 'sub_300', 'sub_450', 'sub_750', 'sub_0', 'other_subscribe']:
        message = call.message
        user_id = message.chat.id
        if user_balance[user_id] >= float(call.data[4:]):
            user_balance[user_id] -= float(call.data[4:])
            cursor.execute('''UPDATE Users SET balance = ? WHERE t_user_chat_id = ?''', user_balance[user_id], user_id)
            conn.commit()
            bot.send_message(user_id, 'Подписка оформлена!\nВаш баланс:{}'.format(user_balance[user_id]))
            show_profile(user_id)

    elif call.data == 'profile':
        show_profile(call.message.chat.id)

    elif call.data == 'pay':
        show_payment_options(call.message.chat.id)

    elif call.data == 'subscribe':
        show_subscribe_options(call.message.chat.id)

    elif call.data == 'info':
        show_bot_info(call.message.chat.id)

    elif call.data == 'stat':
        show_statistics(call.message.chat.id)

    elif call.data == 'support':
        show_support_options(call.message.chat.id)

    elif call.data == 'chats':
        show_chats_info(call.message.chat.id)

    elif call.data == 'addChat':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
        user_data[call.message.chat.id].state = 'add_chat'
        bot.send_message(call.message.chat.id, "Введите название чата.")
    elif call.data == 'deleteChat':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('"Эмпатия машины"', callback_data='deleted_chat'))
        bot.send_message(user_id, 'Какой чат необходимо удалить?', reply_markup=keyboard)

    elif call.data == 'chatsList':
        keyboard = types.InlineKeyboardMarkup()
        cursor.execute('''SELECT * FROM Chats WHERE t_user_chat_id = ?''', user_id)
        result = cursor.fetchall()
        for row in result:
            keyboard.row(types.InlineKeyboardButton(row[1], callback_data=f'chat_info|{row[0]}'))
        bot.send_message(user_id, 'Список чатов:', reply_markup=keyboard)

    elif call.data.startswith('chat_info'):
        chat_id = int(call.data.split('|')[1])
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Список ключевых слов чата', callback_data=f'keywords_list|{chat_id}'))
        keyboard.row(types.InlineKeyboardButton('Добавить ключевые слова', callback_data=f'keywords_add|{chat_id}'))
        keyboard.row(types.InlineKeyboardButton('Удалить ключевые слова', callback_data=f'keywords_delete|{chat_id}'))
        keyboard.row(types.InlineKeyboardButton('Удалить ВСЕ ключевые слова', callback_data=f'all_keywords_delete|{chat_id}'))
        bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)

    elif call.data == 'keywords_add':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
        bot.send_message(user_id, "Введите ключевые слова или фразы через ';'.", reply_markup=keyboard)

    elif call.data == 'keywords_delete':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
        bot.send_message(user_id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)

    elif call.data == 'all_keywords_delete':
        bot.send_message(user_id, "Все ключевые слова чата удалены.")
        show_profile(user_id)

    elif call.data.startswith('keywords_list'):
        chat_id = int(call.data.split('|')[1])
        cursor.execute('''SELECT * FROM Keywords WHERE chat_id = ?''', chat_id)
        result = cursor.fetchone()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
        bot.send_message(user_id, f"Ключевые слова:\n{result[1]}", reply_markup=keyboard)

    elif call.data == 'deleted_chat':
        bot.send_message(user_id, "Чат был удалён.")
        show_profile(user_id)

    else:
        bot.answer_callback_query(call.id, text="Ошибка!")


@bot.poll_handler
def payment_handler(update):
    print(150)
    if update.type == 'payment':
        invoice_payload = update.data['invoice_payload']
        payment_id = update.data['payment_id']

        payment_info = bot.getPayment(payment_id)
        if payment_info['status'] == 'successful':
            # Update user balance
            user_id = payment_info['order_info']['user_id']
            amount = payment_info['total_amount'] / 100  # Convert to rubles
            user_balance[user_id] = round(user_balance[user_id] + float(amount), 2)

            # Send confirmation message
            bot.send_message(user_id, 'Платеж успешно обработан! Ваш баланс обновлен.')
        else:
            # Handle failed payment
            bot.send_message(user_id, 'К сожалению, оплата не прошла. Пожалуйста, попробуйте снова.')

bot.infinity_polling(skip_pending = True)
cursor.close()
print(1)
conn.close()