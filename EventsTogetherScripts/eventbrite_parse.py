from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
from dateparser import parse as dparse
from dateutil import parser
import psycopg2

import cloudinary.uploader

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

query_select = "SELECT 1 FROM app_event WHERE title = %s"

# Запрос на вставку нового события
query_insert = "INSERT INTO app_event (title, description, date, city, place, price_low, price_high, type, image, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

with conn.cursor() as cur:
	for i in range(1, 5):
		webpage = requests.get(f'https://www.eventbrite.com/d/cyprus/all-events/?page={i}')
		soup = BeautifulSoup(webpage.content, "html.parser")
		events = soup.find_all('section', {'class', 'discover-horizontal-event-card'})
		for event in events:
			try:
				title = event.find('h2').text
				date_time = event.find('p').text
				place_with_city = event.find_all('p')[1].text
				place = place_with_city.split('•')[0]
				city = place_with_city.split('•')[1]
				link = event.find('a')['href']
				page = requests.get(link)
				soup_page = BeautifulSoup(page.content, "html.parser")

				info_full = str(soup_page)
				result_low = result_high = '0'  # Default values
				if 'lowPrice' in info_full:
					match = re.search('lowPrice\"\:(.*?)\.', info_full)
					if match:
						result_low = match.group(1)
				if 'highPrice' in info_full:
					match = re.search('highPrice\"\:(.*?)\.', info_full)
					if match:
						result_high = match.group(1)

				description_div = soup_page.find('div', {'class', 'eds-text--left'})
				description = description_div.text if description_div else 'No description'
				img_tag = soup_page.find('img')
				print(img_tag)
				img_url = img_tag['src'] if img_tag else None
				upload_result = cloudinary.uploader.upload(img_url, folder='events')
				uploaded_image_url = upload_result.get('url')
				print(uploaded_image_url)
			except IndexError:
				continue

			updated_date_string = date_time.rstrip(" +1234567890more")

			now = datetime.now()
			tomorrow = now + timedelta(days=1)

			if len(updated_date_string.split(',')) > 2:
				date_string = updated_date_string
				datetime_object = datetime.strptime(date_string, "%a, %b %d, %I:%M %p")
				if datetime_object.year == 1900:
					datetime_object = datetime_object.replace(year=2023)
			else:
				if updated_date_string.lower().startswith("tomorrow"):
					time_part = dparse(updated_date_string.split(" at ")[1])
					datetime_object = tomorrow.replace(hour=time_part.hour, minute=time_part.minute, second=0, microsecond=0)
				elif updated_date_string.lower().startswith("today"):
					time_part = dparse(updated_date_string.split(" at ")[1])
					datetime_object = now.replace(hour=time_part.hour, minute=time_part.minute, second=0, microsecond=0)
				else:
					if updated_date_string.lower() != 'promoted':
						date_string = updated_date_string
						datetime_object = parser.parse(date_string)
						if datetime_object.year == 1900:
							datetime_object = datetime_object.replace(year=2023)
					else:
						datetime_object = None
					if datetime_object.year == 1900:
						datetime_object = datetime_object.replace(year=2023)

			data = (title, description, datetime_object, city[1:], place, result_low, result_high, 'EVENT', uploaded_image_url, 'Cyprus')
			
			cur.execute(query_select, (title,))
			if cur.fetchone() is None:
				cur.execute(query_insert, data)
				conn.commit()

# Close the connection
conn.close()
