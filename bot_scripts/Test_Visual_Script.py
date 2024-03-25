import telebot
from telebot import types


TOKEN = '6534454602:AAH7IlOdqFzRtXAZ2wffIOFpHYFTWdb7-1A'

bot = telebot.TeleBot(TOKEN)
user_balance = {'user_id': 0}
user_data = {}
form = 'pdf'
file_path = ''
cost = 0.2
current_message_number = 1
output_format = None
images_folder = 'D:/Scanner/images'


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in user_balance:
        user_balance[user_id] = float(1000)

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'),
                 types.InlineKeyboardButton('Мониторинг чатов', callback_data='chatsList'))

    bot.send_message(user_id, "Привет! Добро пожаловать в бота.", reply_markup=keyboard)


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
        message = call.message
        user_id = message.chat.id
        user_balance[user_id] = round(user_balance[user_id] + float(call.data), 2)
        bot.send_message(user_id, 'Вы пополнили баланс на {} руб.!'.format(call.data))
        show_profile(user_id)
    elif call.data in ['sub_100', 'sub_300', 'sub_450', 'sub_750', 'sub_0', 'other_subscribe']:
        message = call.message
        user_id = message.chat.id
        if user_balance[user_id] >= float(call.data[4:]):
            user_balance[user_id] -= float(call.data[4:])
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
        bot.send_message(user_id, 'Отправьте ссылку на необходимый чат.', reply_markup=keyboard)
    elif call.data == 'deleteChat':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('"Эмпатия машины"', callback_data='deleted_chat'))
        bot.send_message(user_id, 'Какой чат необходимо удалить?', reply_markup=keyboard)
    elif call.data == 'chatsList':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('"Эмпатия машины"', callback_data='chat_info'))
        bot.send_message(user_id, 'Список чатов:', reply_markup=keyboard)
    elif call.data == 'chat_info':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Список ключевых слов чата', callback_data='keywords_list'))
        keyboard.row(types.InlineKeyboardButton('Добавить ключевые слова', callback_data='keywords_add'))
        keyboard.row(types.InlineKeyboardButton('Удалить ключевые слова', callback_data='keywords_delete'))
        keyboard.row(types.InlineKeyboardButton('Удалить ВСЕ ключевые слова', callback_data='all_keywords_delete'))
        bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)
    elif call.data == 'keywords_add':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
        bot.send_message(user_id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)

    elif call.data == 'keywords_delete':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
        bot.send_message(user_id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)
    elif call.data == 'all_keywords_delete':
        bot.send_message(user_id, "Все ключевые слова чата удалены.")
        show_profile(user_id)
    elif call.data == 'keywords_list':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))
        bot.send_message(user_id, "Ключевые слова:\nкоммерческое", reply_markup=keyboard)
    elif call.data == 'deleted_chat':
        bot.send_message(user_id, "Чат был удалён.")
        show_profile(user_id)
    else:
        bot.answer_callback_query(call.id, text="Ошибка!")


bot.infinity_polling(skip_pending = True)