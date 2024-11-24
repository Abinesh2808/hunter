import asyncio	
from ScrappingHelpers import ScrappingHelpers



class Scrapper:
	def __init__(self):
		self.helper = ScrappingHelpers()
		self.fetched_links = {}

	async def get_links_for_the_products(self, products):
		links = {}

		for keyword in products:
			link = await self.helper.get_product_links(keyword[1])
			links[keyword[0]] = link

		return links


	async def get_links(self, keywords):
		number_of_products = 50
		items = list(keywords.items())

		for i in range(0, len(items), number_of_products):
			chunk = items[i:i + number_of_products]
			self.fetched_links.update(await self.get_links_for_the_products(chunk))


	async def get_title(self, products):
		await self.get_links(products)

		try:
			for url in self.fetched_links:
				await asyncio.gather(*(self.helper.get_product_title(url) for url in self.fetched_links[url]))
				print(f"Title for product {product_id}: {title}")
		except Exception as e:
			print(e)



async def main():
	scrap = Scrapper()
	products = {
		"2ae0b13c": "Kookaburra Kahuna Pro 1.0 Cricket Bat",
		"68f40f6c": "Kookaburra Kahuna Lite Cricket Bat"
	}
	await scrap.get_title(products)

asyncio.run(main())
