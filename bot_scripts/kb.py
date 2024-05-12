from telebot import types

chat_back_keyboard = types.InlineKeyboardMarkup()
chat_back_keyboard.add(types.InlineKeyboardButton('Назад', callback_data='chats'))

keywords_back_keyboard = types.InlineKeyboardMarkup()
keywords_back_keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='chatsList'))

all_keywords_delete_keyboard = types.InlineKeyboardMarkup()
all_keywords_delete_keyboard.row(types.InlineKeyboardButton('Да', callback_data=f'confirm_delete'))
all_keywords_delete_keyboard.row(types.InlineKeyboardButton('Нет', callback_data=f'cancel_delete'))

start_keyboard = types.InlineKeyboardMarkup()
start_keyboard.row(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'),
                 types.InlineKeyboardButton('Мониторинг чатов', callback_data='chats'))

profile_keyboard = types.InlineKeyboardMarkup()
profile_keyboard.add(types.InlineKeyboardButton('О боте', callback_data='info'))
profile_keyboard.add(types.InlineKeyboardButton('Статистика', callback_data='stat'))
profile_keyboard.add(types.InlineKeyboardButton('Поддержка', callback_data='support'))
profile_keyboard.add(types.InlineKeyboardButton('Список чатов', callback_data='chats'))
profile_keyboard.add(types.InlineKeyboardButton('Пополнение баланса', callback_data='pay'))
profile_keyboard.add(types.InlineKeyboardButton('Оформить подписку', callback_data='subscribe'))

payment_keyboard = types.InlineKeyboardMarkup()
payment_keyboard.row(types.InlineKeyboardButton('100 руб', callback_data='100'),
                types.InlineKeyboardButton('300 руб', callback_data='300'),
                types.InlineKeyboardButton('500 руб', callback_data='500'))
payment_keyboard.row(types.InlineKeyboardButton('1000 руб', callback_data='1000'),
                types.InlineKeyboardButton('1500 руб', callback_data='1500'),
                types.InlineKeyboardButton('2000 руб', callback_data='2000'))
payment_keyboard.row(types.InlineKeyboardButton('Отмена', callback_data='profile'))

subscribe_keyboard = types.InlineKeyboardMarkup()
subscribe_keyboard.row(types.InlineKeyboardButton('Фрилансер, 5 чатов, 100 руб/мес', callback_data='sub_100'))
subscribe_keyboard.row(types.InlineKeyboardButton('Стандарт, 15 чатов, 300 руб/мес', callback_data='sub_300'))
subscribe_keyboard.row(types.InlineKeyboardButton('Стартап, 25 чатов, 450 руб/мес', callback_data='sub_450'))
subscribe_keyboard.row(types.InlineKeyboardButton('Компания, 50 чатов, 750 руб/мес', callback_data='sub_750'))
subscribe_keyboard.row(types.InlineKeyboardButton('Бесплатный месяц', callback_data='sub_0'))
subscribe_keyboard.row(types.InlineKeyboardButton('Тарифы на 3мес / 6 мес', callback_data='other_subscribe'))
subscribe_keyboard.row(types.InlineKeyboardButton('Отмена', callback_data='profile'))

support_keyboard = types.InlineKeyboardMarkup()
support_keyboard.add(types.InlineKeyboardButton('Написать в поддержку', url='https://www.google.com'))
support_keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))

profile_back_keyboard = types.InlineKeyboardMarkup()
profile_back_keyboard.add(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))

all_chats_info_keyboard = types.InlineKeyboardMarkup()
all_chats_info_keyboard.row(types.InlineKeyboardButton('Список чатов', callback_data='chatsList'),
                types.InlineKeyboardButton('Добавить чат', callback_data='addChat'),
                types.InlineKeyboardButton('Удалить чат', callback_data='chatDeleteChoice'))
all_chats_info_keyboard.row(types.InlineKeyboardButton('Личный кабинет', callback_data='profile'))

def chat_delete_choice(result):
    chat_delete_choice_keyboard = types.InlineKeyboardMarkup()
    for row in result:
        chat_delete_choice_keyboard.row(types.InlineKeyboardButton(row[1], callback_data=f'deleteChat|{row[0]}'))
    chat_delete_choice_keyboard.add(types.InlineKeyboardButton('Назад', callback_data='chats'))
    return chat_delete_choice_keyboard

def chat_info_inline(chat_id):
    chat_info_inline_keyboard = types.InlineKeyboardMarkup()
    chat_info_inline_keyboard.add(types.InlineKeyboardButton('Назад', callback_data=f'chat_info{chat_id}'))
    return chat_info_inline_keyboard

def chats_list(result):
    chats_list_keyboard = types.InlineKeyboardMarkup()
    for row in result:
        chats_list_keyboard.row(types.InlineKeyboardButton(row[1], callback_data=f'chat_info|{row[0]}'))
        
    chats_list_keyboard.add(types.InlineKeyboardButton('Назад', callback_data='chats'))
    return chats_list_keyboard

def chat_info(chat_id):
    chat_info_keyboard = types.InlineKeyboardMarkup()
    chat_info_keyboard.row(types.InlineKeyboardButton('Список ключевых слов чата', callback_data=f'keywords_list|{chat_id}'))
    chat_info_keyboard.row(types.InlineKeyboardButton('Добавить ключевые слова', callback_data=f'keywords_add|{chat_id}'))
    chat_info_keyboard.row(types.InlineKeyboardButton('Удалить ключевые слова', callback_data=f'keywords_delete|{chat_id}'))
    chat_info_keyboard.row(types.InlineKeyboardButton('Удалить ВСЕ ключевые слова', callback_data=f'all_keywords_delete|{chat_id}'))
    chat_info_keyboard.row(types.InlineKeyboardButton('Назад', callback_data='profile'))
    return chat_info_keyboard
