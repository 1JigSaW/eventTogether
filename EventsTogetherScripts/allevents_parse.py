import os

import psycopg2
import cloudinary.uploader
import time
from dateutil import parser

CLOUD_NAME = os.environ.get('CLOUD_NAME')
API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')

cloudinary.config(
	cloud_name=CLOUD_NAME,
	api_key=API_KEY,
	api_secret=API_SECRET
)

DATABASE_DB = os.environ.get('DATABASE_DB')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_PORT = os.environ.get('DATABASE_PORT')

conn = psycopg2.connect(
	host=DATABASE_HOST,
	database=DATABASE_DB,
	port=DATABASE_PORT,
	user=DATABASE_USER,
	password=DATABASE_PASSWORD
)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
# opts.add_argument('user-agent=' + ua.random)

driver = webdriver.Chrome(options=opts)
urls = [
	'https://allevents.in/limassol/all', 
	'https://allevents.in/nicosia/all',
	'https://allevents.in/famagusta/all',
	'https://allevents.in/strovolos/all',
	'https://allevents.in/lakatamia/all',
	'https://allevents.in/larnaca/all',
	'https://allevents.in/pelentri/all',
	'https://allevents.in/pissouri/all',
	'https://allevents.in/kyrenia/all',
	'https://allevents.in/aglantzia/all',
	'https://allevents.in/germasogeia/all',
	'https://allevents.in/paphos/all',
]

query_select = "SELECT 1 FROM app_event WHERE title = %s"
query_insert = "INSERT INTO app_event (title, description, date, city, place, price_low, price_high, type, image, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

with conn.cursor() as cur:
	for link in urls:
		for attempt in range(3):  # Пытаемся открыть страницу 3 раза
			try:
				driver.get(link)
				break
			except TimeoutException:
				print("Timeout, retrying...")
				if attempt == 2:  # Если это последняя попытка, то прерываем цикл
					print("Failed to load page after 3 attempts, skipping...")
					break
		time.sleep(7)
		cards = driver.find_elements(By.CLASS_NAME, 'event-item')
		for card in cards:
			event_link = card.get_attribute("data-link")
			print(event_link)
			
			driver.execute_script(f"window.open('{event_link}');")
			driver.switch_to.window(driver.window_handles[1])
			time.sleep(5)
			
			try:
				title = driver.find_element(By.CLASS_NAME, 'overlay-h1').text
				print('bd', title)
				description = driver.find_element(By.CLASS_NAME, 'event-description-html').text
				image = driver.find_element(By.CLASS_NAME, 'event-banner-image').get_attribute('src')
				upload_result = cloudinary.uploader.upload(image, folder='events')
				uploaded_image_url = upload_result.get('url')
				print('bd', image)
				num = 1
				try:
					datetime_all = driver.find_elements(By.CLASS_NAME, 'center')[num]
					datetime_text = datetime_all.text.split("\n")[0]  # Используем только первую часть до переноса строки 

					# Если есть " to ", то разделяем на две части, иначе начало и конец одинаковы
					if " to " in datetime_text:
						start_string, end_string = datetime_text.split(" to ", 1)
					else:
						start_string = end_string = datetime_text

					start_string = start_string.replace(" at ", " ")
					start_datetime = parser.parse(start_string)
					print('bd', start_datetime)
				except ValueError:
					num = 0
					datetime_all = driver.find_elements(By.CLASS_NAME, 'center')[num]
					datetime_text = datetime_all.text.split("\n")[0]  # Используем только первую часть до переноса строки 

					# Если есть " to ", то разделяем на две части, иначе начало и конец одинаковы
					if " to " in datetime_text:
						start_string, end_string = datetime_text.split(" to ", 1)
					else:
						start_string = end_string = datetime_text

					start_string = start_string.replace(" at ", " ")
					start_datetime = parser.parse(start_string)
					print('bd', start_datetime)
				place = driver.find_elements(By.CLASS_NAME,'center')[num + 1]
				words = place.text.split(", ")
				unique_words = list(dict.fromkeys(words))

				if 'View on Map' in unique_words:
					unique_words.remove('View on Map')

				clean_place = ", ".join(unique_words)
				clean_place = clean_place.split("\n")[0]
				print('bd', clean_place)

				driver.close()
				driver.switch_to.window(driver.window_handles[0])
			except NoSuchElementException:
				print("Could not find some elements, skipping event")
				driver.close()
				driver.switch_to.window(driver.window_handles[0])

			data = (title, description, start_datetime, clean_place, clean_place, None, None, 'EVENT', uploaded_image_url, 'Cyprus')
				
			cur.execute(query_select, (title,))
			if cur.fetchone() is None:
				cur.execute(query_insert, data)
				conn.commit()


		time.sleep(5) 

		# # Нажимаем на "Show More"
		# wait = WebDriverWait(driver, 10)
		# show_more = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-round')))
		# show_more.click()
conn.close()
driver.quit()
