import urllib.request
from bs4 import BeautifulSoup
from PIL import Image as pil_image
import xlsxwriter
import time
import random

"""
url_begining_1 = 'https://livolo.ru.aliexpress.com/store/group/EU-Touch-Switch/500715_251019193/'
url_end_1 = '.html?spm=a2g0v.12010612.0.0.lUHNmy&origin=n&SortType=bestmatch_sort&g=y'

url_begining_2 = 'https://livolo.ru.aliexpress.com/store/group/EU-Push-Switch-Socket/500715_211913633/'
url_end_2 = '.html?spm=a2g0v.12010612.0.0.HH5z9S&origin=n&SortType=bestmatch_sort&g=y'

url_begining_3 = 'https://livolo.ru.aliexpress.com/store/group/EU-DIY-Parts/500715_253315139/'
url_end_3 = '.html?spm=a2g0v.12010612.0.0.kWqmus&origin=n&SortType=bestmatch_sort&g=y'
"""
url_list = [
   'https://livolo.ru.aliexpress.com/store/group/EU-Touch-Switch/500715_251019193/1.html?spm=a2g0v.12010612.0.0.NKpqLZ&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-Touch-Switch/500715_251019193/2.html?spm=a2g0v.12010612.0.0.X0cZse&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-Push-Switch-Socket/500715_211913633/1.html?spm=a2g0v.12010612.0.0.HH5z9S&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-Push-Switch-Socket/500715_211913633/2.html?spm=a2g0v.12010612.0.0.DUjGXr&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-Push-Switch-Socket/500715_211913633/3.html?spm=a2g0v.12010612.0.0.raPpLG&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-Push-Switch-Socket/500715_211913633/4.html?spm=a2g0v.12010612.0.0.VcYV1j&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-DIY-Parts/500715_253315139/1.html?spm=a2g0v.12010612.0.0.SMetXJ&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-DIY-Parts/500715_253315139/2.html?spm=a2g0v.12010612.0.0.DZTJqa&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-DIY-Parts/500715_253315139/3.html?spm=a2g0v.12010612.0.0.1czfXE&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-DIY-Parts/500715_253315139/4.html?spm=a2g0v.12010612.0.0.4sZg9a&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-DIY-Parts/500715_253315139/5.html?spm=a2g0v.12010612.0.0.Xgz9E9&origin=n&SortType=bestmatch_sort&g=y',
   'https://livolo.ru.aliexpress.com/store/group/EU-DIY-Parts/500715_253315139/6.html?spm=a2g0v.12010612.0.0.lXFxba&origin=n&SortType=bestmatch_sort&g=y'
]

i = 1


def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def parse(html, ws, link_format, list_numb):
    global i

    soup = BeautifulSoup(html)
    ul = soup.find('ul', class_='items-list util-clearfix')

    for layer in ul.find_all('li'):
        div_detail = layer.find('div', class_='detail')
        div_cost = div_detail.find('div', class_='cost')
        title_name = div_detail.h3.a.get('title')
        title_link = 'https:' + div_detail.h3.a.get('href')
        cost = div_cost.text

        div_pic = layer.find('div', class_='pic')
        image_link = div_pic.a.img.get('image-src')
        image_name = str(i) + '-' + str(list_numb) + '.jpg'
        image_link_tmp = image_link[-16:]
        image_link = image_link[:-16]
        image_link = 'https:' + image_link + image_link_tmp[-4:]

        img = urllib.request.urlopen(image_link).read()
        out = open(image_name, "wb")
        out.write(img)
        out.close

        img = pil_image.open(image_name)
        image_name = image_name[:-4] + '.png'
        img = img.resize((300, 300))
        img.save(image_name, 'PNG')

        ws.set_row(2*i, 225)

        ws.write_url(2*i, 0, title_link, link_format, title_name)
        ws.insert_image(2*i, 1, image_name)
        ws.write_url(2*i - 1, 1, image_link, link_format, 'Ссылка')
        ws.write(2*i, 2, cost)
        i += 1


workbook = xlsxwriter.Workbook('EU-DIY-Parts.xlsx')
link_format = workbook.add_format({'color': 'blue', 'underline': 0, 'align': 'center'})
worksheet1 = workbook.add_worksheet('EU-DIY-Parts')
"""
worksheet2 = workbook.add_worksheet('EU-Push-Switch-Socket')
worksheet3 = workbook.add_worksheet('EU-DIY-Parts')
"""

worksheet1.write(0, 0, 'Наименование товара')
worksheet1.write(0, 1, 'Картинка')
worksheet1.write(0, 2, 'Цена')
for k in range(6):
    print(k + 6)
    parse(get_html(url_list[k + 6]), worksheet1, link_format, 3)
    time.sleep(random.randint(5, 25))
"""
worksheet2.set_column(0, 75)
worksheet2.set_column(1, 323)
worksheet2.set_column(2, 25)

worksheet2.write(0, 0, 'Наименование товара')
worksheet2.write(0, 1, 'Картинка')
worksheet2.write(0, 2, 'Цена')

i = 1
for k in range(4):
    print(k + 2)
    parse(get_html(url_list[2 + k]), worksheet2, link_format, 2)
    time.sleep(random.randint(5, 25))

worksheet3.set_column(0, 75)
worksheet3.set_column(1, 323)
worksheet3.set_column(2, 25)

worksheet3.write(0, 0, 'Наименование товара')
worksheet3.write(0, 1, 'Картинка')
worksheet3.write(0, 2, 'Цена')

i = 1
for k in range(6):
    print(k + 6)
    parse(get_html(url_list[6 + k]), worksheet3, link_format, 3)
    time.sleep(random.randint(5, 25))
"""
workbook.close()
