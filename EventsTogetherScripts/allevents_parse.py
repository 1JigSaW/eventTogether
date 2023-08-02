from bs4 import BeautifulSoup
import requests
import psycopg2
import cloudinary.uploader
import re
from datetime import datetime, timedelta
import time
from fake_useragent import UserAgent

cloudinary.config(
	cloud_name = 'dcrvubswi',
	api_key = '296543555619657',
	api_secret = 'zKzEaR92OSUSDh5OtNdZPG4drns'
)

# Connect to the PostgreSQL database
conn = psycopg2.connect(
	host="127.0.0.1",
	database="eventTogether",
	port=5432,
	user="postgres",
	password="Razer197"
)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ua = UserAgent()

# Создаем опции Chrome и меняем user-agent
opts = Options()
opts.add_argument('user-agent=' + ua.random)  # ua.random генерирует случайный действительный user-agent

# Передаем опции при инициализации WebDriver
driver = webdriver.Chrome(options=opts)

driver.get("https://allevents.in/nicosia/all?ref=cityhome")

while True:
	time.sleep(5)
	cards = driver.find_elements(By.CLASS_NAME, 'event-item')
	for card in cards:
		event_link = card.get_attribute("data-link")
		
		# Открываем новую вкладку с ивентом
		driver.execute_script(f"window.open('{event_link}');")
		driver.switch_to.window(driver.window_handles[1])
		time.sleep(5)
		
		try:
			title = driver.find_element(By.CLASS_NAME, 'overlay-h1').text
			print(title)
			description = driver.find_element(By.CLASS_NAME, 'event-description-html').text
			image = driver.find_element(By.CLASS_NAME, 'event-banner-image').get_attribute('src')
			print(image)
			place = driver.find_element('xpath', '//*[@id="event-detail-fade"]/div[1]/div/div[2]/div/div[1]/div[2]/p[1]/span[2]/span')
			print(place.getText())
			datetime_all = driver.find_element('xpath','//*[@id="event-detail-fade"]/div[1]/div/div[2]/div/div[2]/p/span')
			print(datetime_all.getText())
			
			# Закрываем вкладку и переключаемся обратно
			driver.close()
			driver.switch_to.window(driver.window_handles[0])
			break
		except NoSuchElementException:
			print("Could not find some elements, skipping event")
			# Если что-то не нашлось, закрываем вкладку и переключаемся обратно
			driver.close()
			driver.switch_to.window(driver.window_handles[0])

	time.sleep(5)	
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.2);")

	time.sleep(20)  # Пауза для загрузки содержимого страницы

	# Нажимаем на "Show More"
	show_more = driver.find_element_by_css_selector('.btn.load-more-btn')
	show_more.click()

driver.quit()
