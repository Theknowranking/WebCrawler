# web_crawler/web_crawler/spiders/html_crawler.py

import os
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request

class HTMLCrawlerSpider(CrawlSpider):
    name = 'html_crawler'

    def __init__(self, seed_url=None, max_pages=100, max_depth=3, *args, **kwargs):
        super(HTMLCrawlerSpider, self).__init__(*args, **kwargs)
        self.seed_url = seed_url
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)
        self.visited_urls = set()
        # Create html_files folder if it doesn't exist
        os.makedirs('html_files', exist_ok=True)

    def start_requests(self):
        yield Request(url=self.seed_url, callback=self.parse, meta={'depth': 1})

    def parse(self, response):
        depth = response.meta.get('depth', 1)
        if depth > self.max_depth:
            return

        self.visited_urls.add(response.url)

        # Save HTML content
        filename = f'html_files/{response.url.split("/")[-1]}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        # Extract links
        links = LinkExtractor(allow=()).extract_links(response)
        for link in links:
            if link.url not in self.visited_urls:
                yield Request(url=link.url, callback=self.parse, meta={'depth': depth + 1})

        if len(self.visited_urls) >= self.max_pages:
            self.crawler.engine.close_spider(self, 'Reached max pages limit')

    rules = (
        Rule(LinkExtractor(), callback='parse', follow=True),
    )