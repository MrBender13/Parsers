import hashlib
import scrapy
from scrapy.http import Request
from rumetr.scrapy import ApptItem as Item


class Spider(scrapy.Spider):
    name = 'spider'

    start_urls = ['http://www.incom.ru/sale-realty/newbuild/']
    home_url = 'http://www.incom.ru'

    def parse(self, response):
        # parse houses in Moscow
        for href in response.xpath('//a[@class="block"]/@href').extract():
            href = '{}{}/#kvartiry_gk'.format(self.home_url, '/'.join(href.split('/')[:-1]))
            yield response.follow(href, self.parse_buildings)

        # parse houses near Moscow
        for href in response.xpath('//a[@class="block "]/@href').extract():
            href = '{}{}/#kvartiry_gk'.format(self.home_url, '/'.join(href.split('/')[:-1]))
            yield response.follow(href, self.parse_buildings)

    def parse_buildings(self, response):
        complex_name = response.xpath('//h1/text()').extract_first()
        complex_addr = response.xpath('//p[@class="addr"]/a/text()').extract_first()

        # to fix some strange situations when we get different htmls (thanks to server)
        if not complex_addr:
            complex_addr = response.xpath('//p[@class="addr"]/a/span/text()').extract_first()
        complex_addr = ' '.join(complex_addr.split(' ')[1:])

        for href in response.xpath('//div[@data-js-one-korpus-body="1"]/div/span/a/@href').extract():
            # to ignore 'garages'
            ids = href.split('/')[-4:-1]
            if ids[2] != 'apartments':
                continue

            house_url = '{}{}'.format(self.home_url, href)
            request = Request(house_url, callback=self.parse_flats)

            request.meta.update({
                'complex_name': complex_name,
                'complex_id': ids[0],
                'complex_url': response.url,
                'addr': complex_addr,

                'house_id': ids[1],
                'house_url': house_url,
            })

            yield request

    def parse_flats(self, response):
        house_name = response.xpath('//div[@class="newslink noborder cf"]/h2/text()').extract_first()[19:]

        for flat_data in response.xpath('//tr[@style="height: 70px;"]'):
            flat_data = flat_data.xpath('.//span[@data-js-value]/@data-js-value').extract()

            #  to avoid unexpected formats of price
            try:
                flat_price = float(flat_data[7].replace('\t', '').replace('\n', ''))
            except ValueError:
                continue

            yield Item(
                complex_name=response.meta['complex_name'],
                complex_id=response.meta['complex_id'],
                complex_url=response.meta['complex_url'],
                addr=response.meta['addr'],

                house_id=response.meta['house_id'],
                house_name=house_name,
                house_url=response.meta['house_url'],

                id=self.get_flat_id(flat_data),
                floor=flat_data[1],
                room_count=flat_data[3],
                square=flat_data[4],
                price=flat_price,
            )

    @staticmethod
    def get_flat_id(flat_data):
        # returns flat id (if id is missing or incorrect - generates it)
        if flat_data[2] == '' or '.' in flat_data[2]:
            return hashlib.md5('{}{}{}'.format(flat_data[1], flat_data[3], flat_data[4]).encode('utf-8')).hexdigest()
        else:
            return flat_data[2]
