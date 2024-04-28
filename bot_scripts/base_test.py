import pyodbc

# Подключение к базе данных
server = 'DESKTOP-BIV7UD0\SQLEXPRESS01'
database = 'notifications'
username = '<username>'
password = '<password>'
# authentication is optional, please add in if needed
authentication = 'ActiveDirectoryIntegrated' 

conn_string = 'Driver={ODBC Driver 18 for SQL Server}; Server=DESKTOP-BIV7UD0\SQLEXPRESS01; Database=olymp; Trusted_connection=YES;'

# Create the database connection string
conn = pyodbc.connect(
    'driver={ODBC Driver 18 for SQL Server};'
    'Server=DESKTOP-BIV7UD0\SQLEXPRESS01;'
    'Database=notifications;'
    'Trusted_Connection=yes;'
    'Encrypt=optional;'
)

# Создание курсора для выполнения запросов
cursor = conn.cursor()
cursor.execute('''INSERT INTO Users VALUES (?, ?, ?)''', 'dawda', 12341, 1254215)
conn.commit()
cursor.execute('SELECT * FROM Users')
# Получение результатов запроса
results = cursor.fetchall()

# Обработка результатов

for row in results:
    print(row)
    print(row[0])
    print(row[1])

# Закрытие курсора
cursor.close()

# Закрытие соединения с базой данных
conn.close()