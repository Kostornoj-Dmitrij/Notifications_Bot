from config import TOKEN, YOOTOKEN, sub_info, api_id, api_hash
from user import User
from database import cursor, conn
from main import bot, user_balance, user_data, dp
import utils
import kb
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import sys
from aiogram import types
import signal

@dp.message_handler(commands=['start'])
async def start(message:types.Message):
    user_id = message.chat.id
    username = message.chat.username
    if username == None:
        username = 'Notifications'
    cursor.execute('''SELECT * FROM Users WHERE username=?''', (username,))
    result = cursor.fetchone()
    user = User(user_id)
    user_data[user_id] = user
    if not result:
        user_balance[user_id] = float(1000)
        cursor.execute('''INSERT INTO Users (username, t_user_chat_id, balance) VALUES (?, ?, ?)''', (username, user_id, user_balance[user_id],))
        conn.commit()
    else:
        user_balance[user_id] = result[3]

    keyboard = kb.start_keyboard
    await bot.send_message(message.chat.id, "Привет! Добро пожаловать в бота.", reply_markup=keyboard)

@dp.message_handler(lambda message: user_data[message.chat.id].state == 'add_chat')
async def add_link_handler(message): 
    user_data[message.chat.id].chat_link = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=(message.message_id-1))
    if user_data[message.chat.id].chat_link[0] == '@':
        user_data[message.chat.id].chat_link = 'https://t.me/' + user_data[message.chat.id].chat_link[1:]
    user_data[message.chat.id].chat_name = user_data[message.chat.id].chat_link.replace('@', '').replace('https://t.me/', '')   
    new_chat_id = utils.get_group_id(user_data[message.chat.id].chat_link)
    if new_chat_id != 0:
        cursor.execute('''INSERT INTO Chats (chatname, chat_link, t_user_chat_id, lastMessage) VALUES (?, ?, ?, ?)''', (user_data[message.chat.id].chat_name, user_data[message.chat.id].chat_link, message.chat.id, 0,))
        conn.commit()
        await bot.send_message(message.chat.id, f'Чат {user_data[message.chat.id].chat_name} успешно добавлен')
    else:
        await bot.send_message(message.chat.id, f'Не удалось присоединить бота к группе - неверная ссылка!')
    
    
    await utils.show_chats_info(message.chat.id)


@dp.message_handler(lambda message: user_data[message.chat.id].state == 'add_keywords') 
async def add_keywords_handler(message):
    user_data[message.chat.id].keywords = (message.text.replace(' ,', ',').replace(', ', ',')).lower()

    cursor.execute('SELECT keywords FROM KeyWords WHERE chat_id = ? AND user_id = ?', (user_data[message.chat.id].chat_id, user_data[message.chat.id].user_id,))
    existing_keywords = cursor.fetchone()

    if existing_keywords:
        updated_keywords = (existing_keywords[0] + ',' + user_data[message.chat.id].keywords).lower()
        cursor.execute('UPDATE KeyWords SET keywords = ? WHERE chat_id = ? AND user_id = ?', (updated_keywords, user_data[message.chat.id].chat_id, user_data[message.chat.id].user_id,))
    else:
        cursor.execute('INSERT INTO KeyWords (keywords, chat_id, user_id) VALUES (?, ?, ?)', (user_data[message.chat.id].keywords, user_data[message.chat.id].chat_id, user_data[message.chat.id].user_id,))
    
    conn.commit()
    await bot.delete_message(chat_id=message.chat.id, message_id=(message.message_id - 1))
    await bot.send_message(message.chat.id, "Ключевые слова добавлены.")
    
    user_data[message.chat.id].state = 'chat_start'
    callback = user_data[message.chat.id].callback
    callback.data = f'chat_info|{user_data[message.chat.id].chat_id}'
    await callback_inline(callback)


@dp.message_handler(lambda message: user_data[message.chat.id].state == 'keywords_delete') 
async def updated_keywords_handler(message): 
    user_data[message.chat.id].keywords = message.text.lower()
    
    keywords_list = user_data[message.chat.id].keywords.split(',')
    for keyword in keywords_list:
        cursor.execute("UPDATE KeyWords SET keywords = REPLACE(keywords, ?, '') WHERE user_id = ? AND chat_id = ?", (keyword + ',', user_data[message.chat.id].user_id, user_data[message.chat.id].chat_id,))
        cursor.execute("UPDATE KeyWords SET keywords = REPLACE(keywords, ?, '') WHERE user_id = ? AND chat_id = ?", (',' + keyword, user_data[message.chat.id].user_id, user_data[message.chat.id].chat_id,))
    conn.commit()
    await bot.delete_message(chat_id=message.chat.id, message_id=(message.message_id - 1))
    await bot.send_message(message.chat.id, "Ключевые слова удалены.") 
    user_data[message.chat.id].state = 'chat_start'
    callback = user_data[message.chat.id].callback
    callback.data = f'chat_info|{user_data[message.chat.id].chat_id}'
    await callback_inline(callback)


@dp.message_handler(lambda message: True)
async def handle_text(message):
    user_id = message.chat.id
    if message.text == '/profile':
        await utils.show_profile(user_id)
    elif message.text == '/pay':
        await utils.show_payment_options(user_id)
    elif message.text == '/subscribe':
        await utils.show_subscribe_options(user_id)
    elif message.text == '/support':
        await utils.show_support_options(user_id)
    elif message.text == '/info':
        await utils.show_bot_info(user_id)
    elif message.text == '/stat':
        await utils.show_statistics(user_id)
    elif message.text == '/chats':
        await utils.show_chats_info(user_id)
    else:
        await utils.find_message(message, user_id)


@dp.callback_query_handler()
async def callback_inline(call: types.CallbackQuery):
    user_id = call.message.chat.id
    if call.data in ['100', '300', '500', '1000', '1500', '2000']:
        prices = [types.LabeledPrice(label='Руб', amount = int(call.data)*100)]
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await bot.send_invoice(call.message.chat.id, title='Пополнение баланса',
                         description='payment',
                         provider_token=YOOTOKEN, currency='RUB',
                         start_parameter='test_bot', prices=prices, payload='test-invoice-payload')
        
    elif call.data in ['sub_100', 'sub_300', 'sub_450', 'sub_750', 'sub_0', 'other_subscribe']:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        message = call.message
        user_id = message.chat.id
        sub_info_list = sub_info[call.data]
        if user_balance[user_id] >= float(sub_info_list[0]):
            user_balance[user_id] -= float(sub_info_list[0])
            cursor.execute('UPDATE Users SET balance = ? WHERE t_user_chat_id = ?', (user_balance[user_id], user_id,))
            
            cursor.execute("UPDATE Users SET sub_start = DATE('now') WHERE t_user_chat_id = ?", (user_id,))
            cursor.execute('UPDATE Users SET sub_duration = ? WHERE t_user_chat_id = ?', (31, user_id,))
            cursor.execute('UPDATE Users SET chats_constraint = ? WHERE t_user_chat_id = ?', (sub_info_list[1], user_id,))
            conn.commit()
            
            await bot.send_message(user_id, f'Подписка оформлена!\nВаш баланс:{user_balance[user_id]}')
            await utils.show_profile(user_id)
        else:
            await bot.send_message(user_id, 'На балансе недостаточно средств!')
            await utils.show_profile(user_id)
    elif call.data == 'profile':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await utils.show_profile(call.message.chat.id)

    elif call.data == 'pay':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await utils.show_payment_options(call.message.chat.id)

    elif call.data == 'subscribe':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await utils.show_subscribe_options(call.message.chat.id)

    elif call.data == 'info':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await utils.show_bot_info(call.message.chat.id)

    elif call.data == 'stat':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await utils.show_statistics(call.message.chat.id)

    elif call.data == 'support':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await utils.show_support_options(call.message.chat.id)

    elif call.data == 'chats':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await utils.show_chats_info(call.message.chat.id)

    elif call.data == 'addChat':
        
        cursor.execute('SELECT chats_constraint FROM Users WHERE t_user_chat_id = ?', (call.message.chat.id,))
        chats_constraint = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM Chats WHERE t_user_chat_id = ?', (call.message.chat.id,))
        chats_count = cursor.fetchone()[0]
        if chats_count < chats_constraint:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
            keyboard = kb.chat_back_keyboard
            user_data[call.message.chat.id].state = 'add_chat'
            await bot.send_message(call.message.chat.id, "Введите ссылку или id чата.", reply_markup=keyboard)
        else:
            await bot.send_message(call.message.chat.id, "Достигнуто максимальное количество чатов для мониторинга. Повысьте уровень подписки или удалите часть чатов.")
            call.data = 'chats'
            await callback_inline(call)
    elif call.data == 'chatDeleteChoice':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        cursor.execute('''SELECT * FROM Chats WHERE t_user_chat_id = ?''', (user_id,))
        result = cursor.fetchall()
        keyboard = kb.chat_delete_choice(result)
        await bot.send_message(user_id, 'Список чатов:', reply_markup=keyboard)
    
    elif call.data.startswith('deleteChat'):
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        chat_id = int(call.data.split('|')[1])
        keyboard = kb.chat_info_inline(call.data)
        
        cursor.execute('''DELETE FROM Chats WHERE chat_id = ?''', (chat_id,))
        conn.commit()
        await bot.send_message(call.message.chat.id, "Чат был удалён.")
        await utils.show_chats_info(call.message.chat.id)
    elif call.data == 'chatsList':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        user_data[call.message.chat.id].callback = call
        cursor.execute('''SELECT * FROM Chats WHERE t_user_chat_id = ?''', (user_id,))
        result = cursor.fetchall()
        keyboard = kb.chats_list(result)
        await bot.send_message(user_id, 'Список чатов:', reply_markup=keyboard)

    elif call.data.startswith('chat_info'):
        try:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        except:
            pass
        user_data[call.message.chat.id].chat_id = int(call.data.split('|')[1])
        cursor.execute('SELECT * FROM Users WHERE t_user_chat_id = ?', (call.message.chat.id,))
        user_data[call.message.chat.id].user_id = cursor.fetchone()[0]
        keyboard = kb.chat_info(user_data[call.message.chat.id].chat_id)
        await bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)

    elif call.data.startswith('keywords_add'):
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        chat_id = int(call.data.split('|')[1])
        
        keyboard = kb.keywords_back_keyboard
        user_data[call.message.chat.id].state = 'add_keywords'
        await bot.send_message(call.message.chat.id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)

    elif call.data.startswith('keywords_delete'):
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        chat_id = int(call.data.split('|')[1])
        
        keyboard = kb.keywords_back_keyboard
        user_data[call.message.chat.id].state = 'keywords_delete'
        await bot.send_message(call.message.chat.id, "Введите ключевые слова или фразы через запятую.", reply_markup=keyboard)

    elif call.data.startswith('all_keywords_delete'):
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        user_data[call.message.chat.id].chat_id = int(call.data.split('|')[1])
        keyboard = kb.all_keywords_delete_keyboard
        await bot.send_message(user_id, "Вы уверены, что хотите удалить все ключевые слова для данного чата?", reply_markup=keyboard)
    elif call.data.startswith('confirm_delete'):
        cursor.execute("DELETE FROM KeyWords WHERE user_id = ? AND chat_id = ?", (user_data[call.message.chat.id].user_id, user_data[call.message.chat.id].chat_id,))
        conn.commit()
        await bot.send_message(call.message.chat.id, "Все ключевые слова удалены.") 
        user_data[call.message.chat.id].state = 'chat_start'
        call.data = f'chat_info|{user_data[call.message.chat.id].chat_id}'
        await callback_inline(call)
    elif call.data.startswith('cancel_delete'):
        call.data = 'chatsList' 
        await callback_inline(call)
    elif call.data.startswith('keywords_list'):
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        chat_id = int(call.data.split('|')[1])
        cursor.execute('''SELECT * FROM Keywords WHERE chat_id = ?''', (chat_id,))
        result = cursor.fetchone()
        keyboard = kb.chat_info_inline(call.data)
        if result:
            await bot.send_message(user_id, f"Ключевые слова:\n{result[1]}", reply_markup=keyboard)
        else:
            await bot.send_message(user_id, "Чат пока не содержит ключевых слов для поиска.", reply_markup=keyboard)
    elif call.data == 'deleted_chat':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id))
        await bot.send_message(user_id, "Чат был удалён.")
        await utils.show_profile(user_id)
    else:
        await bot.answer_callback_query(call.id, text="Ошибка!")


@dp.shipping_query_handler(lambda query: True)
async def shipping(shipping_query):
    await bot.answer_shipping_query(shipping_query.id, ok=True,
                              error_message='Произошла ошибка.')


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Произошла ошибка.")


@dp.message_handler(content_types=['successful_payment'])
async def got_payment(message):
    amount = message.successful_payment.total_amount / 100
    user_balance[message.chat.id] = round(user_balance[message.chat.id] + float(amount), 2)
    cursor.execute('UPDATE Users SET balance = ROUND(balance + ?, 0) WHERE t_user_chat_id = ?', (amount, message.chat.id,))
    conn.commit()
    await bot.send_message(message.chat.id, f'Баланс был пополнен на {message.successful_payment.total_amount / 100} {message.successful_payment.currency}.')
    await utils.show_profile(message.chat.id)


    
async def monitoring():
    await asyncio.sleep(10)
    while True:
        await client.start()
        cursor.execute('SELECT chat_link FROM Chats')
        links = cursor.fetchall()
        for link in links:
            chat_link = link[0]
            cursor.execute('SELECT lastMessage FROM Chats WHERE chat_link = ?', (chat_link,))
            
            lastMessage = cursor.fetchall()
            if lastMessage == []: 
                continue
            lastMessage = lastMessage[0][0]
            entity = await client.get_entity(chat_link)
            cursor.execute('SELECT keywords_id, keywords, t_user_chat_id, k.chat_id, k.user_id FROM KeyWords k, Users u WHERE chat_id IN (SELECT chat_id FROM Chats WHERE chat_link = ?) AND k.user_id = u.user_id', (chat_link,))
            result = cursor.fetchall()
            messages = await client(GetHistoryRequest(
                peer=entity,
                limit=5,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=lastMessage,
                add_offset=0,
                hash=0
            ))
            for message in messages.messages:
                try:
                    message_text = message.message.lower()
                except:
                    continue
                chat_name = chat_link.split('/')[-1]
                message_link = f"https://t.me/{chat_name}/{message.id}"
                
                message_first_text = ' '.join(message_text.split()[:5])
            
                for keywords in result:
                    flag = False
                    keywords_list = keywords[1].split(',')
                    for keyword in keywords_list:
                        if keyword in message_text:
                            flag = True
                    if flag:
                        cursor.execute("SELECT CASE WHEN DATE(sub_start, '+' || sub_duration || ' day') > CURRENT_DATE THEN 1 ELSE 0 END FROM Users WHERE t_user_chat_id = ?", (keywords[2],))
                        sub_info = cursor.fetchone()[0]
                        if sub_info == 0:
                            try:
                                await bot.send_message(keywords[2], 'Срок вашей подписки закончился. Чтобы продолжить отслеживание, продлите её.')
                            except:
                                pass
                        else:
                            try:
                                await bot.send_message(keywords[2], f'"{chat_name}" пишет: "{message_first_text}..."\nСсылка на полное сообщение: {message_link}')
                            except:
                                pass
                            cursor.execute('INSERT INTO FindMessages (message_link, keywords_id, chat_id, user_id, sender, first_text) VALUES (?, ?, ?, ?, ?, ?)', (message_link, keywords[0], keywords[3], keywords[4], chat_name, message_first_text,))
                            cursor.execute('UPDATE Users SET count_messages = count_messages + 1 WHERE t_user_chat_id = ?', (keywords[2],))
                            conn.commit()
                if message.id > lastMessage:
                    lastMessage = message.id
                    cursor.execute('UPDATE Chats SET lastMessage = ? WHERE chat_link = ?', (lastMessage, chat_link,))
                    conn.commit()
            
            await asyncio.sleep(1)
        await client.disconnect()
        await asyncio.sleep(300)


async def main():
    bot_polling_task =  asyncio.create_task(dp.start_polling(bot))
    async_func_task = asyncio.create_task(monitoring())
    
    await asyncio.gather(bot_polling_task, async_func_task)


client = TelegramClient('anon2', api_id, api_hash)

def stop(signum, frame):
    client.disconnect()
    print("Disconnect")
    sys.exit(0)

signal.signal(signal.SIGINT, stop)
try:
    asyncio.run(main())
finally:
    client.disconnect()