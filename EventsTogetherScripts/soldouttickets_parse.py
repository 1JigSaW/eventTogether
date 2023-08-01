from bs4 import BeautifulSoup
import requests
import psycopg2
import cloudinary.uploader
import re
from datetime import datetime, timedelta

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
query_insert = "INSERT INTO app_event (title, description, date, city, place, price_low, price_high, type, image, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

with conn.cursor() as cur:
	for i in range(1, 10):
		webpage = requests.get(f'https://www.soldoutticketbox.com/easyconsole.cfm/id/324/page_no/{i}/cat_id/0/lang/en')
		soup = BeautifulSoup(webpage.content, "html.parser")

		events = soup.find_all('div', {'class', 'eventBox'})

		for event in events:
			img_tag = event.find('img')
			img_url = 'https://www.soldoutticketbox.com' + img_tag['src'] if img_tag else None
			print(img_url)
			upload_result = cloudinary.uploader.upload(img_url, folder='events')
			uploaded_image_url = upload_result.get('url')
			title = event.find('a', {'class', 'h2Style'}).text
			print(title)
			# date_time = event.find('p').text
			place =  event.find('p', {'class', 'blackSmall'}).text.replace("Where: ", "")
			print(place)
			description = event.find_all('p', {'class', 'blackSmall'})[-1].text
			print(description)
			prices = event.find_all('p', {'class', 'blackSmall'})[-3].text
			prices_obj = re.findall(r'(?:€(\d+)|(\d+)€)(?![^(]*\))', prices)
			try:
				prices_numbers = [int(price[0]) for price in prices_obj]
			except ValueError:
				prices_numbers = [int(price[1]) for price in prices_obj]
			print(prices_numbers)
			# поиск минимального и максимального значения
			try:
				min_price = min(prices_numbers)
				max_price = max(prices_numbers)
			except ValueError:
				min_price = None
				max_price = None
			print(min_price)
			print(max_price)
			print()
			date_str = event.find('p', {'class', 'black'}).text
			match = re.search(r'\d{2}/\d{2}/\d{2}', date_str)
			if match:
				date = match.group(0)
				print(date)
			link = event.find('a')['href']
			page = requests.get('https://www.soldoutticketbox.com' + link)
			soup_page = BeautifulSoup(page.content, "html.parser")
			try:
				time_str = soup_page.find('table', {'class': 'generalEvent'})
				tr_obj = time_str.find_all('tr')[1]
				td_obj = tr_obj.find_all('td')[3].text
				match = re.search(r'\d{2}:\d{2}', td_obj)
				if match:
				    time = match.group()
				    print(time)
			except AttributeError:
				time = None

			if date and time:
			    # Если есть и дата, и время, объединяем их
			    datetime_string = date + " " + time
			    datetime_object = datetime.strptime(datetime_string, "%d/%m/%y %H:%M")  # Обратите внимание на изменение в этой строке
			elif date:
			    # Если есть только дата, мы обрабатываем ее как дату без указания времени
			    datetime_object = datetime.strptime(date, "%d/%m/%y")  # И в этой строке
			elif time:
			    # Если есть только время, мы обрабатываем его как время текущей даты
			    datetime_object = datetime.strptime(time, "%H:%M")
			    datetime_object = datetime.now().replace(hour=datetime_object.hour, minute=datetime_object.minute)
			else:
			    # Если ни дата, ни время не указаны, мы не можем создать объект datetime
			    datetime_object = None


			print(datetime_object)
			data = (title, description, datetime_object, place, place, min_price, max_price, 'EVENT', uploaded_image_url, 'Cyprus')
			
			cur.execute(query_select, (title,))
			if cur.fetchone() is None:
				cur.execute(query_insert, data)
				conn.commit()
		

conn.close()
