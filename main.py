# Подключаем библиотеки
import time
import httplib2
import apiclient.discovery
import json
import psycopg2
import requests
import xml.etree.ElementTree as ET
from oauth2client.service_account import ServiceAccountCredentials

# Данные для авторизации в google
spreadsheetId = "1hEs0dRGvC6zd0u6ViS0biKIsghSaekX2feta1kp-TII" #id таблицы
CREDENTIALS_FILE = "formal-purpose-364109-ca9ad68f591b.json"  # дома
#Данные для подключения к DB
conn = psycopg2.connect( host='90.150.172.84', user='postgres', password='1dcd9ed1', dbname='testdb')
cursor = conn.cursor()

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
#Получение курса USD из ЦБ
def usd():
    usd = float(
        ET.fromstring(requests.get('https://www.cbr.ru/scripts/XML_daily.asp').text)
        .find("./Valute[CharCode='USD']/Value")
        .text.replace(',', '.')
    )
    return usd
# Конвертация доллара в рубли и запись в соседнюю клетку
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
        results = autorized(CREDENTIALS_FILE).spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
            "valueInputOption": "RAW",  # Запись "как есть"
            "data": [
                {"range": f, "values": [
                    x
                ]}
            ]
        }).execute()
        print(f'строка {x[0]} обновлена')
#Запись новых данных в Таблицу google
def write(a,json_read): #(данные авторизации из autorized, данные из файла json read_json)
    results = a.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
        "valueInputOption": "RAW",  # Запись "как есть"
        "data": [
            {"range": 'Лист1!A2:E1000', "values": json_read}
        ]
    }).execute()
# Выводим данные из SQL таблицы
def sql_read(cursor):
    # Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
    cursor.execute("SELECT * FROM test")
    # Получаем результат сделанного запроса
    results = cursor.fetchall()
    return results
# Запись в SQL DB
def sql_write(cursor, text):
    '''with open('data.txt', 'r', encoding='utf-8') as f:  # открыли файл с данными
        text = json.load(f)  # загнали все, что получилось в переменную'''
    for i in text:
        # Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
        cursor.execute(f"""INSERT INTO test VALUES ({i[0]}, {i[1]}, {i[2]}, {"'" + i[3] + "'"}, {i[4]});""")
        conn.commit()
    print('Данные из JSON записаны в Базу данных')
# Очистка таблицы SQL
def sql_del(cursor):
    # Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
    cursor.execute("DELETE FROM test;")
    conn.commit()
    print('Таблица очищена')

while True:
    write_json(read_tab(autorized(CREDENTIALS_FILE), spreadsheetId)) #Запись в JSON
    e = usd_to_rub(read_json(), usd()) #Конвертация usd в rub и запись в соседнюю ячейку
    write_json(e) #Запись новых данных в JSON
    sql_del(cursor) #очистка DB
    sql_write(cursor, read_json()) #запись в DB
    write(autorized(CREDENTIALS_FILE), sql_read(cursor)) #Запись новых данных в Таблицу google
    print('Задача выполнена, данные обновлены')
    time.sleep(0.3) #Пауза для соблюдения кол-ва запросов в минуту (300)