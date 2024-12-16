from ScrappingHelpers import *
import asyncio, aiohttp
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
# from fuzzywuzzy import process
from rapidfuzz import process



class Scrapper:
	def __init__(self):
		self.helpers = ScrappingHelpers()
		self.headers = {
			"User-Agent": self.helpers.generate_random_agent(),
			"Accept-Language": "en-US,en;q=0.9",
			"Referer": "https://www.google.com"
		}
		self.scrapped_products = {}
		self.products_having_issues = {}


	def update_product_issues(self, uid, link, issue):
		if uid not in self.products_having_issues:
			self.products_having_issues[uid] = [{'link': link, 'issue':issue}]
		else:
			self.products_having_issues[uid].append({'link': link, 'issue':issue})


	def get_all_tags(self, page_content):
		tags = {tag.name for tag in page_content.find_all()}
		return tags


	def get_matched_attributes(self, attr_type):
		possibilities = []
		attr_type = attr_type.lower()

		search_terms = {
						'name': ['name'],
						'price': ['mrp', 'price', 'amount', 'product__price', 'product_price']
					}

		attr_with_key = {
						'name':self.name_list,
						'class':self.class_list,
						'id':self.id_list
					}

		for attr_name in search_terms[attr_type]:
			for attr in attr_with_key:
				best_match = process.extractOne(attr_name, attr_with_key[attr])
				if best_match[1] > 80:
					possibilities.append({'key' : attr, 'value' : best_match[0], 'score': best_match[1]})
		
		return possibilities


	def gather_all_element_attributes(self, page_content):
		self.tags = self.get_all_tags(page_content)
		self.id_list = set()
		self.name_list = set()
		self.class_list = set()

		for tag in self.tags:
			for element in page_content.find_all(tag):
				if element.has_attr('id'):
					if len(element['id']) != 0: 
						self.id_list.add(element['id'])

				if element.has_attr('name'):
					if len(element['name']) != 0: 
						self.name_list.add(element['name'])

				if element.has_attr('class'):
					if len(element['class']) != 0: 
						self.class_list.add(" ".join(element['class']))

		possible_name_attributes = self.get_matched_attributes('name')
		possible_price_attributes = self.get_matched_attributes('price')

		return possible_name_attributes, possible_price_attributes



	def get_product_name(self,uid, link, page_content):
		try:
			name_element = page_content.find('h1')
			product_name = name_element.get_text(strip=True)

			if uid not in self.scrapped_products:
				self.scrapped_products[uid] = [{'name': product_name, 'link': link}]
			else:
				self.scrapped_products[uid].append({'name': product_name, 'link': link})

		except Exception as e:
			self.update_product_issues(uid, link, 'Issues in finding product name')
			print(e)

	def get_product_price(self,uid, link, page_content, attributes=None):
		# print("attributes")
		# print(attributes)
		try:
			for attr in attributes:
				key = attr['key']
				value = attr['value']
				price_tags = page_content.find(**{key: value})
				print(f'{key} : {value} - {link}')
				print(price_tags.get_text(strip=True))

			heads = [price_tag.get_text() for price_tag in price_tags if price_tag.name in attributes]
			print("heads")
			print(heads)
			print(heads)
			if uid not in self.scrapped_products:
				self.scrapped_products[uid] = [{'name': product_name, 'link': website_link}]
			else:
				self.scrapped_products[uid].append({'name': product_name, 'link': website_link})
		except Exception as e:
			self.update_product_issues(uid, website_link, 'Issues in finding product price')


	async def get_product_details(self, session, uid, website_link):
		empty_dict = {}

		try:
			async with session.get(website_link, headers=self.headers) as response:
				if response.status == 200:
					try:
						page_data = await response.text()
						soup = BeautifulSoup(page_data, 'html.parser')
						possible_name_attributes, possible_price_attributes = self.gather_all_element_attributes(soup)

						self.get_product_name(uid, website_link, soup)
						self.get_product_price(uid, website_link, soup, possible_price_attributes)


					except Exception as e:
						self.update_product_issues(uid, website_link, 'Issues in finding product details')
				else:
					self.update_product_issues(uid, website_link, 'Page not fetched')

		except Exception as e:
			self.update_product_issues(uid, website_link, 'Something went wrong')


	async def get_google_links(self, uid, pname):
		base_url = 'https://www.google.com'

		async with async_playwright() as driver:
			browser = await driver.chromium.launch(headless=True, args=['--disable-dev-shm-usage'])
			context = await browser.new_context()
			await context.set_extra_http_headers(self.headers)

			page = await context.new_page()
			links = []

			url = u'{}/search?q={}'.format(base_url, requests.utils.quote(pname, safe=';/?:@&=+$,#'))
			print(f"searching for {url}")

			await page.goto(f'{url}')
			await asyncio.sleep(random.randint(1, 3))
			page_contents = await page.content()

			soup = BeautifulSoup(page_contents, 'html.parser')

			try:
				links_container = [h3.parent for h3 in soup.find_all('h3')]

				if not links_container:
					print("here")
					# links_container = tree.xpath('//body/div[2]//a')


				if links_container:
					for element in links_container:
						link = self.helpers.clean_up_url(element.get("href"))
						if link:
							links.append(link)

			except Exception as e:
				self.update_product_issues(uid, website_link, 'URL not fetched from google')
				

			await browser.close()
			return links


	async def scrape_website(self, products_dict):
		# product_links = {}

		# for uid in products_dict:
		# 	product_links[uid] = await self.get_google_links(uid, products_dict[uid])

		product_links = {'cd7f2198': ['https://www.amazon.in/Airavat-Silicone-Comfortable-Bathing-Swimming/dp/B0C39YQQGH', 'https://www.mirusports.com/airavat/swimming/bubble-swimming-cap-purple-adult/cd7f2198?type=product', 'https://www.amazon.in/Airavat-Silicone-Comfortable-Bathing-Swimming/dp/B0C39Y7JRD?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&psc=1&smid=A4QG6CQ8BGXJD', 'https://airavatindia.com/products/bubble-swim-cap', 'https://www.mirusports.com/airavat/swimming/001-swimming-cap-purple-adult/22329e55?type=product', 'https://snooplay.in/products/bubble-silicon-swimming-cap-for-kids-young-adults-grown-ups', 'https://scssports.in/products/airavat-bubble-swimming-cap', 'https://www.sportskhel.com/airavat-classic-single-colour-swimming-cap', 'https://dir.indiamart.com/impcat/speedo-swimming-cap.html'], 'beb1c8d4': ['https://www.amazon.in/Pacer-4-0-Swimming-Goggles-Polycarbonate/dp/B0C4CBCT41', 'https://airavatindia.com/products/pacer-4-0', 'https://www.mirusports.com/airavat/swimming/pacer-4.0-swimming-goggles-blue-adult/beb1c8d4?type=product', 'https://www.sportskhel.com/airavat-1003-frayer-swimming-goggles-blue', 'https://www.amazon.in/stores/AIRAVAT/SwimGoggles_SWIMMING/page/0D6AB021-5455-4F66-8715-231595D20717', 'https://gospree.in/swimming/swimming-accessories/airavat-pacer-4-0-swimming-goggles/', 'https://www.volaresports.com/blogs/news/unveiling-the-vision-choosing-the-right-swimming-goggles-and-lens-colours#:~:text=Clear%20lenses%20are%20ideal%20for%20indoor%2C%20low%2Dlight%20swimming%20or,performance%20in%20various%20lighting%20conditions.', 'https://www.simplyswim.com/blogs/blog/swimming-goggle-guide-choosing-the-right-lenses#:~:text=Blue%3A%20A%20versatile%20choice%2C%20blue,outdoor%20pools%20with%20moderate%20brightness.', 'https://bluebuoy.com/choose-correct-pair-swimming-goggles/#:~:text=There%20are%20three%20important%20factors,swimming%20you%20intend%20to%20do.', 'https://www.speedo.com/blog/swimwear/swimming-goggles-which-lenses-do-i-need/#:~:text=Polarised%20swim%20goggles%20are%20specifically,choice%20for%20all%20weather%20conditions.', 'https://www.ultimatesports.in/categories/swimming-goggles/1646660000029952329', 'https://scssports.in/collections/swimming-goggle', 'https://shaktisportspune.com/product/airavat-pacer-4-0-swimming-goggle/'], 'f3b96b85': ['https://stanford.in/product/classic-750/', 'https://www.tcscricket.com/product/sf-classic-750-kashmir-willow-cricket-bat/', 'https://www.khelmart.com/sf-classic-750-kashmir-willow-cricket-bat', 'https://www.sportswing.in/product/sf-classic-750-kashmir-willow-cricket-bat/', 'https://sportsjam.in/cricket-bats-buyer-guide-choose-cricket-bat', 'https://www.amazon.in/stanford-cricket-bat/s?k=stanford+cricket+bat', 'https://www.talentcricket.co.uk/sf_stanford_cricket_bats/c606.html', 'https://sturdysports.com.au/products/sf-legend-limited-pro-1-0-cricket-bat-senior', 'https://www.totalsf.in/products/sf-classic-750-kashmir-willow-bat-12427267', 'https://www.mirusports.com/sf/cricket/classic-750-cricket-bat-3-kashmir-willow/f3b96b85?type=product', 'https://www.amazon.in/SF-Classic-750-Cricket-BAT/dp/B09RP7VYXX', 'https://kbsportshub.com/products/sf-classic-750-kashmir-willow-cricket-bat', 'https://mahavirsports.co.in/products/sf-classic-750-sh', 'https://shop.kibi.co.in/products/sf-classic-750-cricket-bat-kibi-sports']}


		async with aiohttp.ClientSession() as session:
			for product in product_links:
				tasks = [self.get_product_details(session, product, link) for link in product_links[product]]

				await asyncio.gather(*tasks, return_exceptions=True)


		# print("self.products_having_issues")
		# print(self.products_having_issues)

		# print("self.scrapped_products")
		# print(self.scrapped_products)

































# products = {
# 				'cd7f2198': 'Airavat Bubble Swimming Cap - Purple, Adult',
# 				'beb1c8d4': 'Airavat Pacer 4.0 Swimming Goggles - Blue, Adult',
# 				'f3b96b85': 'SF Classic 750 Cricket Bat - 3, Kashmir Willow',
# 				'36e1f0b6': 'SF Magnum Icon Cricket Bat - SH, English Willow',
# 				'b84dadf5': 'Blaster 8000 Cricket Bat - SH, English Willow',
# 				'4660e9ea': 'DSC Beamer X Cricket Shoes - 11, Blue,White, Mens',
# 				'0050752c': 'Profesional Cricket Sweater  -  38, Off White',
# 				'0061845f': 'GN10 Pro Performence Cricket T-Shirt  -  S, White',
# 				'0000ca9d': 'MITT Cricket Fielding Practice Gloves - Grey',
# 				'0042b0c2': 'Condor Motion Cricket Leg Guard  -  Mens, White, Right-handed'
# 			}

products = {
				'cd7f2198': 'Airavat Bubble Swimming Cap - Purple, Adult',
				'beb1c8d4': 'Airavat Pacer 4.0 Swimming Goggles - Blue, Adult',
				'f3b96b85': 'SF Classic 750 Cricket Bat - 3, Kashmir Willow'
			}


scrapper = Scrapper()
asyncio.run(scrapper.scrape_website(products))