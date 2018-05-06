# coding=utf-8
import hashlib
import scrapy
from rumetr.scrapy import ApptItem as Item

STUDIO = 'Студия'
ONE_ROOM_FLAT = 'Однокомнатная'
TWO_ROOM_FLAT = 'Двухкомнатная'
THREE_ROOM_FLAT = 'Трёхкомнатная'
COMPLEX_NAME = 'ЖК Краски Жизни'
ADDRESS = 'г. Видное, р-н Ленинский, мкр. 5, квартал "Краски жизни"'


class Spider(scrapy.Spider):
    name = 'spider'

    home_url = 'https://kraski-zhizni-vidnoe.ru/kvartiry/'
    start_urls = [home_url]

    def parse(self, response):
        # opening all flats at one table (to do that we need to count flats)
        flats_count = response.xpath('//span[@class="b-search__load-from"]/text()').extract_first()
        flats_count = int(int(flats_count.split('\xa0')[-1:][0]) / 20 + 1)
        url = 'https://kraski-zhizni-vidnoe.ru/kvartiry/?sort=area&order=asc&price[min]=0&price[max]=10+000+000&\
area[min]=29&area[max]=110&floor[min]=1&floor[max]=17&__s=&page={}&object=0'.format(flats_count)
        yield response.follow(url, self.parse_flats)

    def parse_flats(self, response):
        for crt in response.xpath('//tr[@class="j-building-tr-link"]'):
            flat_data = crt.xpath('.//td')

            # getting string with type of flat and amount of rooms
            type_and_id = flat_data[1].xpath('.//a[@class="b-search-results-table__name"]/text()').extract()
            type_and_id = type_and_id[0].strip()
            flat_id = type_and_id.split(' ')[-1:][0]
            is_studio = type_and_id.split(' ')[0] == STUDIO

            # detecting amount of rooms
            rooms_string = type_and_id.split(' ')[0]
            if is_studio or rooms_string == ONE_ROOM_FLAT:
                rooms_amount = 1
            elif rooms_string == TWO_ROOM_FLAT:
                rooms_amount = 2
            elif rooms_string == THREE_ROOM_FLAT:
                rooms_amount = 3

            # getting house name
            house_name = flat_data[1].xpath('.//div/span/text()').extract_first()
            house_name = " ".join(house_name.split(" ")[:2])

            # getting square
            square = flat_data[2].xpath('.//text()').extract()
            square = square[0].replace(',', '.').replace('м', '').strip()

            # getting floor
            floor = flat_data[3].xpath('.//text()').extract()
            floor = floor[0].split('/')[0]

            # getting price
            price = flat_data[4].xpath('.//div[@class="b-search-results-table__price "]/text()').extract_first()
            price = price.strip().split(' ')
            price[-1] = price[-1][:3]
            price = ''.join(price)

            yield Item(
                complex_name=COMPLEX_NAME,
                complex_id=self.generate_id(COMPLEX_NAME),
                complex_url=self.home_url,
                addr=ADDRESS,

                house_id=self.generate_id(house_name),
                house_name=house_name,
                house_url=self.home_url,

                id=flat_id,
                floor=floor,
                room_count=rooms_amount,
                is_studio=is_studio,
                square=square,
                price=price,
            )

    @staticmethod
    def generate_id(string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()
