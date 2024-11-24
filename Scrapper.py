import asyncio	
from ScrappingHelpers import ScrappingHelpers



class Scrapper:
	def __init__(self):
		self.helper = ScrappingHelpers()


	async def get_links_for_the_products(self, products):
		links = {}

		for keyword in products:
			link = await self.helper.get_links(keyword[1])
			links[keyword[0]] = link

		return links


	def get_links(self, keywords):
		number_of_products = 50
		items = list(keywords.items())

		for i in range(0, len(items), number_of_products):
			chunk = items[i:i + number_of_products]
			fetched_links = asyncio.run(self.get_links_for_the_products(chunk))

			print(fetched_links)
			print(len(fetched_links))






scrap = Scrapper()
links = scrap.get_links({"2ae0b13c":"Kookaburra Kahuna Pro 1.0 Cricket Bat",
						"68f40f6c":"Kookaburra Kahuna Lite Cricket Bat"})











