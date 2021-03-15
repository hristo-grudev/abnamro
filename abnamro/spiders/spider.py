import datetime
import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import AbnamroItem
from itemloaders.processors import TakeFirst

base = 'https://www.abnamro.com/api/content-delivery/overview/articles?siteSection=Dotcom&locale=nl-NL&startingIndex={}&limit=100'


class AbnamroSpider(scrapy.Spider):
	name = 'abnamro'
	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		raw_data = json.loads(response.text)
		total_article = raw_data['total']
		for item in raw_data["overviewArticles"]:
			slug = item['slugs'][0]['value']
			url = f'https://www.abnamro.com/api/content-delivery/article/{slug}?locale=nl-NL'

			yield response.follow(url, self.parse_post)

		if self.page < total_article:
			self.page += 100
			yield response.follow(base.format(self.page), self.parse, dont_filter=True)

	def parse_post(self, response):
		raw_data = json.loads(response.text)
		title = raw_data['title']
		description = raw_data['introduction']
		if raw_data['mainText']:
			for nii in raw_data['mainText']['content']:
				try:
					description += nii['content'][0]['value']
				except:
					pass
		date = raw_data['publicationDate']
		date = datetime.datetime.fromtimestamp(date / 1000.0)

		item = ItemLoader(item=AbnamroItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
