import scrapy
import requests
from rumetr.scrapy import ApptItem as Item


class NDVSpider(scrapy.Spider):
    #имя бота
    name = 'ndv'

    #стартовая станица для парсинга
    start_urls = ['https://www.ndv.ru/novostrojki']
    #домашняя страница сайта
    home_url = 'https://www.ndv.ru'

    #начало работы паука
    def parse(self, response):
        #со стартовой страницы извлекаем ссылки на все ЖК и переходим по ним
        for href in response.xpath('//div[@class="tile__head"]/a/@href').extract():
            url = '{}{}/available-flats'.format(self.home_url, href)
            yield response.follow(url, self.parse_building)

    #обработка конкретного ЖК
    def parse_building(self, response):
        #извлекаем адрес ЖК
        comlex_addr = response.xpath('//div[@class="complex-info__city"]/span/text()').extract_first()

        #извлекаем id ЖК
        complex_id = response.xpath('//input[@id="complexId"]/@value').extract_first()

        #получаем количество квартир в ЖК
        flats_amount = requests.get('https://www.ndv.ru/ajax/flat/listCount?filter%5Bcomplex_id%5D={}'.format(complex_id)).text
        flats_amount = flats_amount[1:-1]

        #получаем список квартир в формате json
        flats_data = requests.get('https://www.ndv.ru/ajax/flat/list?filter%5Bcomplex_id%5D={}&limit%5Blimit%5D={}'.format(complex_id, flats_amount)).json()
        
        for flat in flats_data:
            yield Item(
                 complex_name=flat['complexTitle'],
                 complex_id=flat['complex_id'],
                 complex_url=response.url,
                 addr=comlex_addr,

                 house_id=flat['housing_id'],
                 house_name=flat['housing_title'],
                 house_url='{}?filter%5Bhousing_number%5D={}'.format(response.url, flat['number']),

                 id=flat['id'],
                 floor=flat['floor'],
                 room_count=flat['rooms_number'],
                 square=flat['area'],
                 price=round(float(flat['price']))
            )
