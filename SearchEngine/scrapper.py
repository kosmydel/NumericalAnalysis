import scrapy

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://en.wikipedia.org/wiki/England']

    def parse(self, response):
        for title in response.css('.firstHeading'):
            yield {'title': title.css('::text').get()}

        for next_page in response.css('a'):
            yield response.follow(next_page, self.parse)