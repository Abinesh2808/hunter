import asyncio,json,time,random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup	
from httpx import AsyncClient, Response



class ScrappingHelpers:
	def __init__(self):
		self.client = AsyncClient(headers = {
			"Accept-Language": "en-US,en;q=0.9",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
		})

	def cleanup_url(self, url):
		cleaned_url = url.split("?srsltid")[0].split("&srsltid")
		return cleaned_url[0]

	async def get_product_links(self, keyword):
		links = []

		async with async_playwright() as playwright:
			browser = await playwright.chromium.launch(headless=True)
			page = await browser.new_page()
			pages_needed = 5

			for page_number in range(1, pages_needed):
				await page.goto(f'https://www.google.com/search?q="{keyword}"&start={str((page_number-1) * 10)}')
				await asyncio.sleep(random.uniform(1, 3))
				page_contents = await page.content()
				# time.sleep(random.uniform(1, 3))

				soup = BeautifulSoup(page_contents, 'html.parser')
				link_elements = soup.find_all('div', class_="yuRUbf")

				for element in link_elements:
					try:
						links.append(self.cleanup_url(element.a.get("href")))
					except AttributeError:
						...

		return links


	async def get_product_title(self, url):
		print("url")
		print(url)
		page = await self.client.get(url)

		try:
			soup = BeautifulSoup(page.text, 'html.parser')
			h1_tags_in_body = soup.body.find_all('h1')
			for h1 in h1_tags_in_body:
				if 'Kookaburra Kahuna' in h1.get_text():
					print(h1.get_text())
		except Exception as e:
			print(f"Failed to fetch details for {e}")

# asyncio.run(get_links("Kookaburra Kahuna Pro 1.0 Cricket Bat - SH, English Willow"))