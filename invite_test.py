import requests

# Замените YOUR_BOT_TOKEN на ваш токен бота
bot_token = '7190849200:AAEWkxqFuCHKxaI-sRTvGDnKvG1xktjIv_A'

# Замените CHANNEL_USERNAME на юзернейм канала, например @channel_username
channel_username = 'testNotifications12'

# Формируем URL для запроса к Telegram Bot API

# Формируем URL для запроса обновлений
url = f'https://api.telegram.org/bot{bot_token}/getUpdates'

# Отправляем GET запрос к API Telegram
response = requests.get(url)

# Получаем данные из ответа
data = response.json()

# Печатаем полученные данные
print(data)

