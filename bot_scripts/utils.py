from main import bot, user_balance, user_data
from database import cursor, conn
from config import TOKEN
import kb
import re
import requests


def plural_words(n, words):
    if n % 10 > 4 or n % 10 == 0 or 11 < n < 15:
        return words[2]
    if n % 10 == 1:
        return words[0]
    return words[1]     
    

def show_profile(user_id):
    cursor.execute('SELECT DATEDIFF(day, GETDATE(), DATEADD(day, sub_duration, sub_start)) FROM Users WHERE t_user_chat_id = ?', user_id)
    time_left = cursor.fetchone()[0]
    if time_left <= 0: sub_status = 'неактивна.'
    else: sub_status = 'активна.'
    balance = user_balance[user_id]
    keyboard = kb.profile_keyboard
    bot.send_message(user_id, f"Подписка {sub_status}\nВаш баланс: {balance} руб", reply_markup=keyboard)


def show_payment_options(user_id):
    keyboard = kb.payment_keyboard
    bot.send_message(user_id, "Выберите сумму для пополнения:", reply_markup=keyboard)


def show_subscribe_options(user_id):
    cursor.execute('SELECT DATEDIFF(day, GETDATE(), DATEADD(day, sub_duration, sub_start)) FROM Users WHERE t_user_chat_id = ?', user_id)
    time_left = cursor.fetchone()[0]
    keyboard = kb.subscribe_keyboard
    if time_left <= 0:
        bot.send_message(user_id, f"У вас нет активной подписки.\nВарианты подписки:", reply_markup=keyboard)
    else:
        bot.send_message(user_id, f"Ваша подписка действует ещё {time_left} {plural_words(time_left, ['день', 'дня', 'дней'])}.\nВарианты подписки:", reply_markup=keyboard)


def show_support_options(user_id):
    keyboard = kb.support_keyboard

    bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)


def show_bot_info(user_id):
    keyboard = kb.profile_back_keyboard
    bot.send_message(user_id, "Это бот для уведомлений.", reply_markup=keyboard)


def show_statistics(user_id):
    cursor.execute('SELECT count_messages FROM Users WHERE t_user_chat_id = ?', user_id)
    count_messages = cursor.fetchone()[0]
    keyboard = kb.profile_back_keyboard
    bot.send_message(user_id, f"Статистика:\nКоличество найденных сообщений за время работы - {count_messages}", reply_markup=keyboard)


def show_chats_info(user_id):
    cursor.execute('SELECT COUNT(chat_id) FROM Chats WHERE t_user_chat_id = ?', (user_id))
    user_data[user_id].chat_id = cursor.fetchone()[0]
    keyboard = kb.all_chats_info_keyboard
    bot.send_message(user_id, f"Включенных в мониторинг чатов - {user_data[user_id].chat_id}", reply_markup=keyboard)


def get_group_id(link):
    match = re.search(r"https://t.me/([\w\d_-]+)", link)
    if match:
        group_name = match.group(1)
        url = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={group_name}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["result"]["id"]
    else:
        return 0


def find_message(message, chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={chat_id}"
    response = requests.get(url)
    data = response.json()
    if data["ok"]:
        bot_username = data["result"]["username"]
        chat_link = f"https://t.me/{bot_username}"
    else:
        chat_link = ""
    cursor.execute('SELECT keywords_id, keywords, t_user_chat_id, k.chat_id, k.user_id FROM KeyWords k, Users u WHERE chat_id IN (SELECT chat_id FROM Chats WHERE chat_link = ?) AND k.user_id = u.user_id', chat_link)
    result = cursor.fetchall()
    message_text = message.text.lower()
    message_link = f"https://t.me/{message.chat.username}/{message.message_id}"
    chat_name = message.chat.title
    message_first_text = ' '.join(message_text.split()[:5])
    
    for keywords in result:
        flag = False
        keywords_list = keywords[1].split(',')
        for keyword in keywords_list:
            if keyword in message_text:
                flag = True
        if flag:
            cursor.execute('SELECT CASE WHEN DATEADD(day, sub_duration, sub_start) > GETDATE() THEN 1 ELSE 0 END FROM Users WHERE t_user_chat_id = ?', keywords[2])
            sub_info = cursor.fetchone()[0]
            if sub_info == 0:
                bot.send_message(keywords[2], 'Срок вашей подписки закончился. Чтобы продолжить отслеживание, продлите её.')
            else:
                bot.send_message(keywords[2], f'"{chat_name}" пишет: "{message_first_text}..."\nСсылка на полное сообщение: {message_link}')
                cursor.execute('INSERT INTO FindMessages (t_message_link, keywords_id, chat_id, user_id, sender, first_text) VALUES (?, ?, ?, ?, ?, ?)', (message_link, keywords[0], keywords[3], keywords[4], chat_name, message_first_text))
                cursor.execute('UPDATE Users SET count_messages = count_messages + 1 WHERE t_user_chat_id = ?', keywords[2])
                conn.commit()

