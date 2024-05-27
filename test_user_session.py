import asyncio

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

import sqlite3

dbfile = 'data\database.db'

conn = sqlite3.connect(dbfile, check_same_thread=False)

cursor = conn.cursor()


api_id = 25343481
api_hash = "1b9b1920da970fe963043d31382bdf5c"

client = TelegramClient('anon2', api_id, api_hash)
client.disconnect()
print("Disconnect")
"""
async def monitoring():
    await client.start()
    while True:
        print(1)
    '''
    messages_id = {}
    while True:
        cursor.execute('SELECT chat_link FROM Chats')
        links = cursor.fetchall()
        for link in links:
            link = link[0]
            if link not in messages_id:
                messages_id[link] = 0
            entity = await client.get_entity(link)
            cursor.execute('SELECT keywords_id, keywords, t_user_chat_id, k.chat_id, k.user_id FROM KeyWords k, Users u WHERE chat_id IN (SELECT chat_id FROM Chats WHERE chat_link = ?) AND k.user_id = u.user_id', (link,))
            result = cursor.fetchall()
            messages = await client(GetHistoryRequest(
                peer=entity,
                limit=10,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=messages_id[link],
                add_offset=0,
                hash=0
            ))
            for message in messages.messages:
                message_text = message.message.lower()
                chat_name = link.split('/')[-1]
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
                            print('Срок вашей подписки закончился. Чтобы продолжить отслеживание, продлите её.')
                        else:
                            print(f'"{chat_name}" пишет: "{message_first_text}..."\nСсылка на полное сообщение: {message_link}')
                            cursor.execute('INSERT INTO FindMessages (message_link, keywords_id, chat_id, user_id, sender, first_text) VALUES (?, ?, ?, ?, ?, ?)', (message_link, keywords[0], keywords[3], keywords[4], chat_name, message_first_text,))
                            cursor.execute('UPDATE Users SET count_messages = count_messages + 1 WHERE t_user_chat_id = ?', (keywords[2],))
                            conn.commit()
                if message.id > messages_id[link]:
                    messages_id[link] = message.id
        print('-------------------------------------------------------')
        await asyncio.sleep(300)
        '''

async def stop():
    await client.disconnect()
    print("Disconnected")

try:
    asyncio.run(monitoring())
except KeyboardInterrupt:
    asyncio.run(stop())
"""