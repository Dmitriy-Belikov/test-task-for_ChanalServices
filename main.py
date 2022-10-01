# Подключаем библиотеки
import datetime
import httplib2
import apiclient.discovery
import json
import psycopg2
import requests
import xml.etree.ElementTree as ET
from google.protobuf import service
from oauth2client.service_account import ServiceAccountCredentials
from psycopg2 import OperationalError
from pycbrf.toolbox import ExchangeRates
from googleapiclient import discovery
from pprint import pprint

# Данные для авторизации
spreadsheetId = "1hEs0dRGvC6zd0u6ViS0biKIsghSaekX2feta1kp-TII"
# CREDENTIALS_FILE = 'formal-purpose-364109-a5b34def6819.json'  # на работе Имя файла с закрытым ключом, вы должны подставить свое
CREDENTIALS_FILE = "formal-purpose-364109-ca9ad68f591b.json"  # дома


# Читаем ключи из файла
def autorized(CREDENTIALS_FILE):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    return service
# Чтение таблицы
def read_tab(service, spreadsheetId):
    ranges = ["Лист1!A2:D1000"]  #

    results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                       ranges=ranges,
                                                       valueRenderOption='FORMATTED_VALUE',
                                                       dateTimeRenderOption='FORMATTED_STRING').execute()
    sheet_values = results['valueRanges'][0]['values']
    # print(sheet_values)
    return sheet_values
# Запись JSON
def write_json(data):
    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile)
# Чтение JSON
def read_json():
    with open('data.txt', 'r', encoding='utf-8') as f:  # открыли файл с данными
        text = json.load(f)  # загнали все, что получилось в переменную
        # pprint(text) #вывели результат на экран
    return text
# Конвертация доллара в рубли и запись в соседнюю клетку
def usd():
    usd = float(
        ET.fromstring(requests.get('https://www.cbr.ru/scripts/XML_daily.asp').text)
        .find("./Valute[CharCode='USD']/Value")
        .text.replace(',', '.')
    )
    return usd
def usd_to_rub(text, doll):
    new_data = []
    for i in text:
        usd = i[2]  # цена в USD
        rub = int(usd) * doll  # цена в рублях
        rub = round(rub, 2)
        i.append(str(rub))
        new_data.append(i)
    return new_data
#Ублюдсое записывание в таблицу google
def ubludok(spreadsheetId):
    p = 0
    for i in range(2,len(read_json())+2):
        x = read_json()[0+p]
        p += 1

        f = 'Лист1!A' + str(i) + ':E' + str(i)
        results = a.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
            "valueInputOption": "RAW",  # Запись "как есть"
            "data": [
                {"range": f, "values": [
                    x
                ]}
            ]
        }).execute()
        print(f'строка {x[0]} обновлена')
def write(a,json_read):
    results = a.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "RAW",  # Запись "как есть"
        "data": [
            {"range": 'Лист1!A2:E1000', "values": json_read}
        ]
    }).execute()
'''a = autorized(CREDENTIALS_FILE)  # Авторизация
b = read_tab(a, spreadsheetId) #Чтение таблицы
c = write_json(b) #Запись в JSON
d = read_json() #Чтение JSON
e = usd_to_rub(d, usd()) #Конвертация usd в rub и запись в соседнюю ячейку
f = write_json(e) #Запись новых данных в JSON
g = read_json() #Чтение JSON
write(a, g) #Запись новых данных в Таблицу google
print('Задача выполнена, данные обновлены')'''
conn = psycopg2.connect( )
cursor = conn.cursor()
def sql_read(cursor):
    # Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
    cursor.execute("SELECT * FROM test")
    # Получаем результат сделанного запроса
    results = cursor.fetchall()
    print(results)
def sql_write(cursor):
    # Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
    cursor.execute("INSERT INTO test VALUES (1, 1249708, 675, 'ggg', 37326.62);")
    conn.commit()
def sql_del(cursor):
    # Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
    cursor.execute("DELETE FROM test;")
    conn.commit()
def sql_write_tets(cursor):
    with open('data.txt', 'r', encoding='utf-8') as f:  # открыли файл с данными
        text = json.load(f)  # загнали все, что получилось в переменную
    for i in text:
        # Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
        cursor.execute(f"INSERT INTO test VALUES ({i[0]}, {i[1]}, {i[2]}, {i[3]}, {i[4]});")
        conn.commit()
sql_write_tets(cursor)
sql_read(cursor)


'''sql_del(cursor)
sql_write(cursor)
sql_read(cursor)'''