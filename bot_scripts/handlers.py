from telebot import types
from config import TOKEN, YOOTOKEN, sub_info
from user import User
from database import cursor, conn
from main import bot, user_balance, user_data
import utils
import kb


@bot.message_handler(commands=['start'])
@bot.channel_post_handler(commands=['start'])
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

    keyboard = kb.start_keyboard
    bot.send_message(user_id, "Привет! Добро пожаловать в бота.", reply_markup=keyboard)


@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'add_chat')
@bot.channel_post_handler(func=lambda message: user_data[message.chat.id].state == 'add_chat')
def add_chat_handler(message): 
    user_data[message.chat.id].chat_name = message.text 
    user_data[message.chat.id].state = 'add_link'
    bot.send_message(message.chat.id, "Теперь введите ссылку на чат.")


@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'add_link')
@bot.channel_post_handler(func=lambda message: user_data[message.chat.id].state == 'add_link')
def add_link_handler(message): 
    
    user_data[message.chat.id].chat_link = message.text
    new_chat_id = utils.get_group_id(user_data[message.chat.id].chat_link)
    if new_chat_id != 0:
        cursor.execute('''INSERT INTO Chats (chatname, chat_link, t_user_chat_id, t_chat_id) VALUES (?, ?, ?, ?)''', user_data[message.chat.id].chat_name, user_data[message.chat.id].chat_link, message.chat.id, new_chat_id)
        conn.commit()
        bot.send_message(message.chat.id, f'Чат {user_data[message.chat.id].chat_name} успешно добавлен')
    else:
        bot.send_message(message.chat.id, f'Не удалось присоединить бота к группе - неверная ссылка!')
    utils.show_chats_info(message.chat.id)


@bot.message_handler(func=lambda message: user_data[message.chat.id].state == 'add_keywords') 
@bot.channel_post_handler(func=lambda message: user_data[message.chat.id].state == 'add_keywords') 
def add_keywords_handler(message):
    user_data[message.chat.id].keywords = (message.text.replace(' ,', ',').replace(', ', ',')).lower()

    cursor.execute('SELECT keywords FROM KeyWords WHERE chat_id = ? AND user_id = ?', (user_data[message.chat.id].chat_id, user_data[message.chat.id].user_id))
    existing_keywords = cursor.fetchone()

    if existing_keywords:
        updated_keywords = (existing_keywords[0] + ',' + user_data[message.chat.id].keywords).lower()
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
@bot.channel_post_handler(func=lambda message: user_data[message.chat.id].state == 'keywords_delete') 
def updated_keywords_handler(message): 
    user_data[message.chat.id].keywords = message.text.lower()
    
    keywords_list = user_data[message.chat.id].keywords.split(',')
    for keyword in keywords_list:
        cursor.execute("UPDATE KeyWords SET keywords = REPLACE(keywords, ?, '') WHERE user_id = ? AND chat_id = ?", (keyword + ',', user_data[message.chat.id].user_id, user_data[message.chat.id].chat_id))
        cursor.execute("UPDATE KeyWords SET keywords = REPLACE(keywords, ?, '') WHERE user_id = ? AND chat_id = ?", (',' + keyword, user_data[message.chat.id].user_id, user_data[message.chat.id].chat_id))
    conn.commit()
    bot.send_message(message.chat.id, "Ключевые слова удалены.") 
    user_data[message.chat.id].state = 'chat_start'
    callback = user_data[message.chat.id].callback
    callback.data = f'chat_info|{user_data[message.chat.id].chat_id}'
    callback_inline(callback)


@bot.message_handler(func=lambda message: True)
@bot.channel_post_handler(func=lambda message: True)
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
    else:
        utils.find_message(message, user_id)


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
        sub_info_list = sub_info[call.data]
        if user_balance[user_id] >= float(sub_info_list[0]):
            user_balance[user_id] -= float(sub_info_list[0])
            cursor.execute('UPDATE Users SET balance = ? WHERE t_user_chat_id = ?', user_balance[user_id], user_id)
            
            cursor.execute('UPDATE Users SET sub_start = GETDATE() WHERE t_user_chat_id = ?', user_id)
            cursor.execute('UPDATE Users SET sub_duration = ? WHERE t_user_chat_id = ?', 31, user_id)
            cursor.execute('UPDATE Users SET chats_constraint = ? WHERE t_user_chat_id = ?', sub_info_list[1], user_id)
            conn.commit()
            bot.send_message(user_id, f'Подписка оформлена!\nВаш баланс:{user_balance[user_id]}')
            utils.show_profile(user_id)
        else:
            bot.send_message(user_id, 'На балансе недостаточно средств!')
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
        cursor.execute('SELECT chats_constraint FROM Users WHERE t_user_chat_id = ?', call.message.chat.id)
        chats_constraint = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM Chats WHERE t_user_chat_id = ?', call.message.chat.id)
        chats_count = cursor.fetchone()[0]
        if chats_count < chats_constraint:
            keyboard = kb.chat_back_keyboard
            user_data[call.message.chat.id].state = 'add_chat'
            bot.send_message(call.message.chat.id, "Введите название чата.", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, "Достигнуто максимальное количество чатов для мониторинга. Повысьте уровень подписки или удалите часть чатов.")

    elif call.data == 'chatDeleteChoice':
        cursor.execute('''SELECT * FROM Chats WHERE t_user_chat_id = ?''', user_id)
        result = cursor.fetchall()
        keyboard = kb.chat_delete_choice(result)
        bot.send_message(user_id, 'Список чатов:', reply_markup=keyboard)
    
    elif call.data.startswith('deleteChat'):
        chat_id = int(call.data.split('|')[1])
        keyboard = kb.chat_info_inline(call.data)
        
        cursor.execute('''DELETE FROM Chats WHERE chat_id = ?''', chat_id)
        conn.commit()
        bot.send_message(call.message.chat.id, "Чат был удалён.")
        utils.show_chats_info(call.message.chat.id)
    elif call.data == 'chatsList':
        
        user_data[call.message.chat.id].callback = call
        cursor.execute('''SELECT * FROM Chats WHERE t_user_chat_id = ?''', user_id)
        result = cursor.fetchall()
        keyboard = kb.chats_list(result)
        bot.send_message(user_id, 'Список чатов:', reply_markup=keyboard)

    elif call.data.startswith('chat_info'):
        
        user_data[call.message.chat.id].chat_id = int(call.data.split('|')[1])
        cursor.execute('SELECT * FROM Users WHERE t_user_chat_id = ?', call.message.chat.id)
        user_data[call.message.chat.id].user_id = cursor.fetchone()[0]
        keyboard = kb.chat_info(user_data[call.message.chat.id].chat_id)
        bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)

    elif call.data.startswith('keywords_add'):
        chat_id = int(call.data.split('|')[1])
        
        keyboard = kb.keywords_back_keyboard
        user_data[call.message.chat.id].state = 'add_keywords'
        bot.send_message(call.message.chat.id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)

    elif call.data.startswith('keywords_delete'):
        chat_id = int(call.data.split('|')[1])
        
        keyboard = kb.keywords_back_keyboard
        user_data[call.message.chat.id].state = 'keywords_delete'
        bot.send_message(call.message.chat.id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)

    elif call.data.startswith('all_keywords_delete'):
        user_data[call.message.chat.id].chat_id = int(call.data.split('|')[1])
        keyboard = kb.all_keywords_delete_keyboard
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
        keyboard = kb.chat_info_inline(call.data)
        if result:
            bot.send_message(user_id, f"Ключевые слова:\n{result[1]}", reply_markup=keyboard)
        else:
            bot.send_message(user_id, "Чат пока не содержит ключевых слов для поиска.", reply_markup=keyboard)
    elif call.data == 'deleted_chat':
        bot.send_message(user_id, "Чат был удалён.")
        utils.show_profile(user_id)
    else:
        bot.answer_callback_query(call.id, text="Ошибка!")


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    bot.answer_shipping_query(shipping_query.id, ok=True,
                              error_message='Произошла ошибка.')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Произошла ошибка.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    amount = message.successful_payment.total_amount / 100
    user_balance[message.chat.id] = round(user_balance[message.chat.id] + float(amount), 2)
    cursor.execute('UPDATE Users SET balance = ROUND(balance + ?, 0) WHERE t_user_chat_id = ?', amount, message.chat.id)
    conn.commit()
    bot.send_message(message.chat.id, f'Баланс был пополнен на {message.successful_payment.total_amount / 100} {message.successful_payment.currency}.')
    utils.show_profile(message.chat.id)
     
            
bot.infinity_polling(skip_pending = True)