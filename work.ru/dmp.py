import requests
from bs4 import BeautifulSoup as BS
import xlsxwriter
import re

requests.packages.urllib3.disable_warnings()

home_url = 'https://work.ru/'

url = r'https://work.ru/cvlist.php?Keywords=%D0%BC%D0%B5%D0%BD%D0%B5%D0%B4%D0%B6%D0%B5%D1%80+%D0%BF%D0%BE+%D0%BF%D1%80%D0%BE%D0%B4%D0%B0%D0%B6%D0%B0%D0%BC&PayFrom=20000&PayTo=25000&ListPage='

summary_numb = 0


def get_html(url):
    response = requests.get(url, verify=False)
    return response.text


def get_page_numb(url):
    soup = BS(get_html(url), 'lxml')

    tr = soup.find('tr', {'class': 'navigator'})
    return int(tr.td.div.text[-21:])


def parse_summary(url):
    soup = BS(get_html(url), 'lxml')

    div_cont = soup.find('div', {'id': 'contacts'})
    mail = re.compile('Email: .+?\n').search(div_cont.text)
    if not mail:
        mail = ''
    else:
        mail = mail.group(0)[7:-1]

    number = re.compile('Телефон: .+?E|телефон .+?\n').search(div_cont.text)
    if not number:
        number = ''
    else:
        number = number.group(0)[9:-1]

    """div_info = soup.find('div', {'id': 'info'})
    name = re.compile('ФИО: .+?\n').search(div_info.text)
    age = re.compile('Возраст: .+?\n').search(div_info.text)
    expiriense = re.compile('Стаж: .+?\n').search(div_info.text)
    print(name.group(0))
    print(age.group(0))
    print(expiriense.group(0))"""
    return (mail, number)


def parse(url, w_s, l_f):
    global home_url
    global summary_numb
    soup = BS(get_html(url), 'lxml')

    tbody = soup.find('table', {'class': 'grid'})
    del soup

    all_tr = tbody.find_all('tr')[:-1]

    for tr in all_tr:
        summary_numb += 1
        name = tr.td.a.text  # специальность
        summary_url = home_url + tr.td.a.get('href')  # ссылка на резюме

        compensation = tr.th.p.text  # зарплата
        region = tr.th.div.text  # область

        email, phone = parse_summary(summary_url)  # email

        w_s.write_url(summary_numb, 0, summary_url, l_f, name)
        w_s.write(summary_numb, 1, compensation)
        w_s.write(summary_numb, 2, region)
        w_s.write(summary_numb, 3, email)
        w_s.write(summary_numb, 4, phone)


workbook = xlsxwriter.Workbook('Data.xlsx')
link_format = workbook.add_format({'color': 'blue', 'underline': 0})
title_format = workbook.add_format({'bold': True, 'align': 'centre'})
worksheet = workbook.add_worksheet('Summary')

worksheet.set_column(0, 0, 85)
worksheet.set_column(1, 1, 16)
worksheet.set_column(2, 2, 25)
worksheet.set_column(3, 3, 24)
worksheet.set_column(4, 4, 18)
worksheet.write(0, 0, 'Должность (Cсылка на резюме)', title_format)
worksheet.write(0, 1, 'Желаемая З/П', title_format)
worksheet.write(0, 2, 'Область', title_format)
worksheet.write(0, 3, 'Email', title_format)
worksheet.write(0, 4, 'Контактный номер', title_format)

page_numb = get_page_numb(url + str(1))
for i in range(800):
    print('Обрабатываем страницу № ' + str(i + 1))
    parse(url + str(i + 1), worksheet, link_format)

print('Записано ' + str(summary_numb) + ' резюме')
workbook.close()
