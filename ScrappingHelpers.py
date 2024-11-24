import asyncio,json,time,random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup	
from httpx import AsyncClient, Response



class ScrappingHelpers:
	def __init__(self):
		...

	def cleanup_url(self, url):
		cleaned_url = url.split("?srsltid")[0].split("&srsltid")
		return cleaned_url[0]

	async def get_links(self, keyword):
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

# asyncio.run(get_links("Kookaburra Kahuna Pro 1.0 Cricket Bat - SH, English Willow"))