import scrapy
from scrapy.http import Request
from simplejson import loads
from rumetr.scrapy import ApptItem as Item


class NDVSpider(scrapy.Spider):
    name = 'ndv'

    start_urls = ['https://www.ndv.ru/novostrojki']
    home_url = 'https://www.ndv.ru'

    def parse(self, response):
        for href in response.xpath('//div[@class="tile__head"]/a/@href').extract():
            url = '{}{}/available-flats'.format(self.home_url, href)
            yield response.follow(url, self.parse_building)

    def parse_building(self, response):
        complex_addr = response.xpath('//div[@class="complex-info__city"]/span/text()').extract_first()

        complex_id = response.xpath('//input[@id="complexId"]/@value').extract_first()

        request = Request('https://www.ndv.ru/ajax/flat/listCount?filter%5Bcomplex_id%5D={}'.format(complex_id),
                          callback=self.get_flats_amount)
        request.meta.update({
            'complex_addr': complex_addr,
            'complex_id': complex_id,
            'our_url': response.url
            })

        yield request

    def get_flats_amount(self, response):
        flats_amount = response.text[1:-1]

        request = Request('https://www.ndv.ru/ajax/flat/list?filter%5Bcomplex_id%5D={}&limit%5Blimit%5D={}'.format(response.meta['complex_id'], flats_amount),
                          callback=self.form_item)
        request.meta.update({
            'complex_addr': response.meta['complex_addr'],
            'complex_id': response.meta['complex_id'],
            'our_url': response.meta['our_url']
        })

        yield request

    def form_item(self, response):
        for flat in loads(response.body_as_unicode()):
            yield Item(
                 complex_name=flat['complexTitle'],
                 complex_id=flat['complex_id'],
                 complex_url=response.meta['our_url'],
                 addr=response.meta['comlex_addr'],

                 house_id=flat['housing_id'],
                 house_name=flat['housing_title'],
                 house_url='{}?filter%5Bhousing_number%5D={}'.format(response.meta['our_url'], flat['number']),

                 id=flat['id'],
                 floor=flat['floor'],
                 room_count=flat['rooms_number'],
                 square=flat['area'],
                 price=round(float(flat['price']))
            )
