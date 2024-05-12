import pyodbc

conn = pyodbc.connect(

    'driver={ODBC Driver 18 for SQL Server};'
    'Server=DESKTOP-BIV7UD0\SQLEXPRESS01;'
    'Database=notifications;'
    'Trusted_Connection=yes;'
    'Encrypt=optional;'
)

cursor = conn.cursor()