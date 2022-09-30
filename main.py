# Подключаем библиотеки
import httplib2
import apiclient.discovery
import json
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

#Данные для авторизации
spreadsheetId = "1hEs0dRGvC6zd0u6ViS0biKIsghSaekX2feta1kp-TII"
CREDENTIALS_FILE = 'formal-purpose-364109-a5b34def6819.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
def autorized(spreadsheetId, CREDENTIALS_FILE):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    return service

#Чтение таблицы
def read_tab(service):
    ranges = ["Лист1!A2:F8"]  #

    results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                   ranges=ranges,
                                                   valueRenderOption='FORMATTED_VALUE',
                                                   dateTimeRenderOption='FORMATTED_STRING').execute()
    sheet_values = results['valueRanges'][0]['values']
    #print(sheet_values)
    return sheet_values
#data = read_tab(autorized(spreadsheetId, CREDENTIALS_FILE))
"""with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)"""

with open('data.txt', 'r', encoding='utf-8') as f: #открыли файл с данными
    text = json.load(f) #загнали все, что получилось в переменную
    #pprint(text) #вывели результат на экран
new_data = []
for i in text:
    usd = i[2] #цена в USD
    rub = int(usd) * 60 #цена в рублях
    i.append(str(rub))
    #print(i)
    obr = new_data.append(i)
print(new_data)
