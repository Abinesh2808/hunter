import asyncio,json,time,random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup	
from httpx import AsyncClient, Response
from fake_useragent import UserAgent



class ScrappingHelpers:
	def __init__(self):
		self.user_agent = UserAgent()

	def clean_up_url(self, url):
		cleaned_url = url.split("?srsltid")[0].split("&srsltid")

		return self.user_agent.random



		if 'mirusports' not in cleaned_url[0]:
			return cleaned_url[0]

	def generate_random_agent(self):
		return self.user_agent.random