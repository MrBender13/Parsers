import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re


root_dir = os.path.abspath(os.curdir)  # папка запуска скрипта
list_dir = os.listdir()  # список файлов в текущей директории
i = 0
while i < len(list_dir):  # оставляем только директории
    if list_dir[i].find('.') != -1:
        del list_dir[i]
    i += 1

base_url = 'https://pubg.me/player/'


#  возвращает html по url
def get_html(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})  # формаруем запрос
    return urlopen(req).read()


#  обработчик строки
def to_string(string):
    if not re.search('[a-z]', string):
        return ''.join(x for x in string if (x.isdigit()) or x == '.')

    if string.find('km') != -1 or string.find(' m') != -1:
        return ''.join(x for x in string if (x.isdigit()) or x == '.')

    d = string.split()[0]
    if d[-1] == 'm':
        return d[:-1]

    h = string.split()[1]
    if d[-1] == 'd':
        return str(int(d[:-1]) * 24 + int(h[:-1]))

    return h[:-1]


def get_names(url):
    result = ''

    soup = BeautifulSoup(get_html(url), "lxml")  # создаём объект на основе html

    total_stat = soup.find('div', class_='card mb-3 mt-1 profile-header-card')
    total_stat = total_stat.find_all('div', class_='profile-header-stats d-flex flex-column justify-content-center')  # общая информация профиля

    additional_stat = soup.find('div', class_='col col-main')
    additional_stat = additional_stat.find_all('div', class_='col-md-4')  # много информации о squad-fpp

    del soup

    stat = total_stat + additional_stat
    del total_stat, additional_stat

    for column in stat:
        labels = column.find_all('div', class_='label')
        for label in labels:
            result += ','
            result += '"' + label.text + '"'

    result += '\n'
    return '"player_name"' + result


stat_name = get_names(base_url + 'ollywood' + '/squad-fpp')
len_names = len(stat_name)


#  парсим сайт
def parse(url, file):
    try:
        soup = BeautifulSoup(get_html(url), "lxml")  # создаём объект на основе html

        total_stat = soup.find('div', class_='card mb-3 mt-1 profile-header-card')
        total_stat = total_stat.find_all('div', class_='profile-header-stats d-flex flex-column justify-content-center')  # общая информация профиля

        additional_stat = soup.find('div', class_='col col-main')
        additional_stat = additional_stat.find_all('div', class_='col-md-4')  # много информации о squad-fpp

        del soup

        stat = total_stat + additional_stat
        del total_stat, additional_stat

        for column in stat:
            values = column.find_all('div', class_='value')
            for value in values:
                file.write(',')
                file.write(to_string(value.text))
    except HTTPError:
        global len_names
        file.write(',0'*(len_names - 4))
        return

for direct in list_dir:
    os.chdir(direct)  # заходим в папку с комндой
    players_file = open('players.txt', 'r')  # открываем файл с игроками
    fpp_squad_stat = open('squad_fpp_stat.csv', 'w')  # открываем файл для записи статистики

    fpp_squad_stat.write(stat_name)

    i = 1
    for player in players_file.readlines():
        if player[-1] == '\n':
            player = player[:-1]

        fpp_squad_stat.write('"' + player + '"')
        parse(base_url + player + '/squad-fpp', fpp_squad_stat)
        if i != 4:
            fpp_squad_stat.write('\n')
        i += 1
    os.chdir(root_dir)  # возвращаемся в базовую директорию
    print(direct + ' ends')
