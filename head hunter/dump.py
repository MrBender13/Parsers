from urllib import request
from bs4 import BeautifulSoup as BS
import xlsxwriter

home_url = 'https://spb.hh.ru'

url = input('Введите ссылку: ')

summary_numb = 0


def get_html(url):
    response = request.urlopen(url)
    return response.read().decode('utf-8')


def parse(url, w_s, l_f):
    global home_url
    global summary_numb
    soup = BS(get_html(url), 'lxml')

    table = soup.find('div', {'class': 'bloko-column_m-9'})
    del soup

    table_summary = table.find('table', {'class': 'output'})

    table_summary = table_summary.find_all('td', {'class': 'output__main-cell'})

    for summary in table_summary:
        summary_numb += 1
        output_main = summary.find('div', {'class': 'output__main'})

        name = output_main.span.a.text  # специальность
        summary_url = home_url + output_main.span.a.get('href')  # ссылка на резюме

        try:
            expiriense = output_main.find('div', {'class': 'output__experience-sum'}).text  # опыт работы
        except AttributeError:
            expiriense = ''

        output_indent = output_main.find('div', {'class': 'output__indent'})

        try:
            position = output_indent.div.span.text  # должность на прошлой работе работы
        except AttributeError:
            position = ''

        try:
            company = output_indent.strong.text  # место последней работы
        except AttributeError:
            company = ''

        compensation = summary.find('span', {'class': 'output__compensation'}).text[:-14]  # зарплата
        age = summary.find('span', {'class': 'output__age'}).text[18:]  # возраст

        w_s.write_url(summary_numb, 0, summary_url, l_f, name)
        w_s.write(summary_numb, 1, expiriense)
        w_s.write(summary_numb, 2, position)
        w_s.write(summary_numb, 3, company)
        w_s.write(summary_numb, 4, compensation)
        w_s.write(summary_numb, 5, age)

    try:
        next_page = table.find('a', {'data-qa': 'pager-next'}).get('href')
        return home_url + next_page
    except AttributeError:
        return None


workbook = xlsxwriter.Workbook('Data.xlsx')
link_format = workbook.add_format({'color': 'blue', 'underline': 0})
title_format = workbook.add_format({'bold': True, 'align': 'centre'})
worksheet = workbook.add_worksheet('Summary')

worksheet.set_column(0, 0, 60)
worksheet.set_column(1, 1, 20)
worksheet.set_column(2, 2, 40)
worksheet.set_column(3, 3, 40)
worksheet.set_column(4, 4, 15)
worksheet.set_column(5, 5, 10)
worksheet.write(0, 0, 'Должность (Cсылка на резюме)', title_format)
worksheet.write(0, 1, 'Опыт работы', title_format)
worksheet.write(0, 2, 'Последнее место работы (Должность)', title_format)
worksheet.write(0, 3, 'Последнее место работы', title_format)
worksheet.write(0, 4, 'Желаемая З/П', title_format)
worksheet.write(0, 5, 'Возраст', title_format)

page_numb = 0
while True:
    page_numb += 1

    print('Обрабатываем страницу № ' + str(page_numb))
    next_url = parse(url, worksheet, link_format)
    if not next_url:
        break
    url = next_url


print('Записано ' + str(summary_numb) + ' резюме')
workbook.close()
