import telebot
from telebot import types
from config import TOKEN, YOOTOKEN, KEYWORDS_LIST
from user import User
from database import cursor, conn
from main import bot, user_balance, user_data
import utils

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    username = message.chat.username
    if username == None:
        username = 'Notifications'
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
                 types.InlineKeyboardButton('Мониторинг чатов', callback_data='chats'))
    user_data[1390442427].chat_id = 1
    user_data[1390442427].user_id = 1
    user_data[1390442427].keywords_id = 1
    print(user_data)
    bot.send_message(user_id, "Привет! Добро пожаловать в бота.", reply_markup=keyboard)

@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'add_chat') 
def add_chat_handler(message): 
    user_data[message.chat.id].chat_name = message.text 
    user_data[message.chat.id].state = 'add_link'
    bot.send_message(message.chat.id, "Теперь введите ссылку на чат.")

@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'add_link') 
def add_link_handler(message): 
    
    user_data[message.chat.id].chat_link = message.text
    try:
        cursor.execute('''INSERT INTO Chats (chatname, chat_link, t_user_chat_id) VALUES (?, ?, ?)''', user_data[message.chat.id].chat_name, user_data[message.chat.id].chat_link, message.chat.id)
        conn.commit()
        bot.send_message(message.chat.id, f'Чат {user_data[message.chat.id].chat_name} успешно добавлен')
    except Exception as e:
        bot.send_message(message.chat.id, f'Не удалось присоединить бота к группе: {e}')
    utils.show_chats_info(message.chat.id)

@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'add_keywords') 
def add_keywords_handler(message):
    user_data[message.chat.id].keywords = message.text.replace(' ,', ',').replace(', ', ',')

    cursor.execute('SELECT keywords FROM KeyWords WHERE chat_id = ? AND user_id = ?', (user_data[message.chat.id].chat_id, user_data[message.chat.id].user_id))
    existing_keywords = cursor.fetchone()

    if existing_keywords:
        updated_keywords = existing_keywords[0] + ',' + user_data[message.chat.id].keywords
        cursor.execute('UPDATE KeyWords SET keywords = ? WHERE chat_id = ? AND user_id = ?', (updated_keywords, user_data[message.chat.id].chat_id, user_data[message.chat.id].user_id))
    else:
        cursor.execute('INSERT INTO KeyWords (keywords, chat_id, user_id) VALUES (?, ?, ?)', (user_data[message.chat.id].keywords, user_data[message.chat.id].chat_id, user_data[message.chat.id].user_id))
    
    conn.commit() 
     
    bot.send_message(message.chat.id, "Ключевые слова добавлены.") 
    user_data[message.chat.id].state = 'chat_start'
    callback = user_data[message.chat.id].callback
    callback.data = f'chat_info|{user_data[message.chat.id].chat_id}'
    callback_inline(callback)

@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'keywords_delete') 
def add_chat_handler(message): 
    user_data[message.chat.id].keywords = message.text
    
    keywords_list = user_data[message.chat.id].keywords.split(',')
    for keyword in keywords_list:
        cursor.execute("UPDATE KeyWords SET keywords = REPLACE(keywords, ?, '') WHERE user_id = ? AND chat_id = ?", (keyword + ',', user_data[message.chat.id].user_id, user_data[message.chat.id].chat_id))
    conn.commit()
    bot.send_message(message.chat.id, "Ключевые слова удалены.") 
    user_data[message.chat.id].state = 'chat_start'
    callback = user_data[message.chat.id].callback
    callback.data = f'chat_info|{user_data[message.chat.id].chat_id}'
    callback_inline(callback)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    if message.text == '/profile':
        utils.show_profile(user_id)
    elif message.text == '/pay':
        utils.show_payment_options(user_id)
    elif message.text == '/subscribe':
        utils.show_subscribe_options(user_id)
    elif message.text == '/support':
        utils.show_support_options(user_id)
    elif message.text == '/info':
        utils.show_bot_info(user_id)
    elif message.text == '/stat':
        utils.show_statistics(user_id)
    elif message.text == '/chats':
        utils.show_chats_info(user_id)
    elif message.text == '/test':
        bot.send_message(user_id, '"Эмпатия машины" пишет: "xAI опубликовала исходный код модели..."\nСсылка на полное сообщение: https://t.me/c/1948713469/106')
    else:
        utils.find_message(message, 1390442427)


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
            utils.show_profile(user_id)

    elif call.data == 'profile':
        utils.show_profile(call.message.chat.id)

    elif call.data == 'pay':
        utils.show_payment_options(call.message.chat.id)

    elif call.data == 'subscribe':
        utils.show_subscribe_options(call.message.chat.id)

    elif call.data == 'info':
        utils.show_bot_info(call.message.chat.id)

    elif call.data == 'stat':
        utils.show_statistics(call.message.chat.id)

    elif call.data == 'support':
        utils.show_support_options(call.message.chat.id)

    elif call.data == 'chats':
        utils.show_chats_info(call.message.chat.id)

    elif call.data == 'addChat':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Назад', callback_data='chats'))
        user_data[call.message.chat.id].state = 'add_chat'
        bot.send_message(call.message.chat.id, "Введите название чата.", reply_markup=keyboard)

    elif call.data == 'chatDeleteChoice':
        
        keyboard = types.InlineKeyboardMarkup()
        cursor.execute('''SELECT * FROM Chats WHERE t_user_chat_id = ?''', user_id)
        result = cursor.fetchall()
        for row in result:
            keyboard.row(types.InlineKeyboardButton(row[1], callback_data=f'deleteChat|{row[0]}'))
        keyboard.add(types.InlineKeyboardButton('Назад', callback_data='chats'))
        bot.send_message(user_id, 'Список чатов:', reply_markup=keyboard)
    
    elif call.data.startswith('deleteChat'):
        
        chat_id = int(call.data.split('|')[1])
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Назад', callback_data=f'chat_info{call.data}'))
        cursor.execute('''DELETE FROM Chats WHERE chat_id = ?''', chat_id)
        conn.commit()
        bot.send_message(call.message.chat.id, "Чат был удалён.")
        utils.show_chats_info(call.message.chat.id)
    elif call.data == 'chatsList':
        
        user_data[call.message.chat.id].callback = call
        
        keyboard = types.InlineKeyboardMarkup()
        cursor.execute('''SELECT * FROM Chats WHERE t_user_chat_id = ?''', user_id)
        result = cursor.fetchall()
        for row in result:
            keyboard.row(types.InlineKeyboardButton(row[1], callback_data=f'chat_info|{row[0]}'))
        
        keyboard.add(types.InlineKeyboardButton('Назад', callback_data='chats'))
        bot.send_message(user_id, 'Список чатов:', reply_markup=keyboard)

    elif call.data.startswith('chat_info'):
        
        user_data[call.message.chat.id].chat_id = int(call.data.split('|')[1])
        cursor.execute('SELECT * FROM Users WHERE t_user_chat_id = ?', call.message.chat.id)
        user_data[call.message.chat.id].user_id = cursor.fetchone()[0]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Список ключевых слов чата', callback_data=f'keywords_list|{user_data[call.message.chat.id].chat_id}'))
        keyboard.row(types.InlineKeyboardButton('Добавить ключевые слова', callback_data=f'keywords_add|{user_data[call.message.chat.id].chat_id}'))
        keyboard.row(types.InlineKeyboardButton('Удалить ключевые слова', callback_data=f'keywords_delete|{user_data[call.message.chat.id].chat_id}'))
        keyboard.row(types.InlineKeyboardButton('Удалить ВСЕ ключевые слова', callback_data=f'all_keywords_delete|{user_data[call.message.chat.id].chat_id}'))
        keyboard.row(types.InlineKeyboardButton('Назад', callback_data='profile'))
        bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)

    elif call.data.startswith('keywords_add'):
        chat_id = int(call.data.split('|')[1])
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='chatsList'))
        user_data[call.message.chat.id].state = 'add_keywords'
        bot.send_message(call.message.chat.id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)

    elif call.data.startswith('keywords_delete'):
        chat_id = int(call.data.split('|')[1])
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='chatsList'))
        user_data[call.message.chat.id].state = 'keywords_delete'
        bot.send_message(call.message.chat.id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)

    elif call.data.startswith('all_keywords_delete'):
        user_data[call.message.chat.id].chat_id = int(call.data.split('|')[1])
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Да', callback_data=f'confirm_delete'))
        keyboard.row(types.InlineKeyboardButton('Нет', callback_data=f'cancel_delete'))
        bot.send_message(user_id, "Вы уверены, что хотите удалить все ключевые слова для данного чата?", reply_markup=keyboard)
    elif call.data.startswith('confirm_delete'):
        cursor.execute("DELETE FROM KeyWords WHERE user_id = ? AND chat_id = ?", (user_data[call.message.chat.id].user_id, user_data[call.message.chat.id].chat_id))
        conn.commit()
        bot.send_message(call.message.chat.id, "Все ключевые слова удалены.") 
        user_data[call.message.chat.id].state = 'chat_start'
        call.data = f'chat_info|{user_data[call.message.chat.id].chat_id}'
        callback_inline(call)
    elif call.data.startswith('cancel_delete'):
        call.data = 'chatsList' 
        callback_inline(call)
    elif call.data.startswith('keywords_list'):
        chat_id = int(call.data.split('|')[1])
        cursor.execute('''SELECT * FROM Keywords WHERE chat_id = ?''', chat_id)
        result = cursor.fetchone()
        if result:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data=f'chat_info{call.data}'))
            bot.send_message(user_id, f"Ключевые слова:\n{result[1]}", reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data=f'chat_info{call.data}'))
            bot.send_message(user_id, "Чат пока не содержит ключевых слов для поиска.", reply_markup=keyboard)
    elif call.data == 'deleted_chat':
        bot.send_message(user_id, "Чат был удалён.")
        utils.show_profile(user_id)

    else:
        bot.answer_callback_query(call.id, text="Ошибка!")


@bot.poll_handler
def payment_handler(update):

    if update.type == 'payment':
        invoice_payload = update.data['invoice_payload']
        payment_id = update.data['payment_id']

        payment_info = bot.getPayment(payment_id)
        if payment_info['status'] == 'successful':
            
            user_id = payment_info['order_info']['user_id']
            amount = payment_info['total_amount'] / 100 
            user_balance[user_id] = round(user_balance[user_id] + float(amount), 2)

           
            bot.send_message(user_id, 'Платеж успешно обработан! Ваш баланс обновлен.')
        else:
     
            bot.send_message(user_id, 'К сожалению, оплата не прошла. Пожалуйста, попробуйте снова.')
bot.infinity_polling(skip_pending = True)