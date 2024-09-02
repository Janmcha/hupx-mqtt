import requests
import json
import pandas as pd
import paho.mqtt.client as mqtt
import datetime
from datetime import date, timedelta

debug = False
today = date.today()
tomorrow = date.today()+timedelta(days=1)

#mqtt definitions
ip = "10.36.4.6"
username = "mqtt"
password = "mqtt"



def avg_extremes_index_of_three(numbers):

	# Check if the list has at least three elements
	if len(numbers) < 3:
		raise ValueError("The list must contain at least three numbers.")

	# Initialize variables to keep track of the lowest and highest averages and their indices
	min_average = float('inf')  # Start with an infinitely large value
	max_average = float('-inf')  # Start with an infinitely small value
	min_index = -1  # Initialize to an invalid index
	max_index = -1  # Initialize to an invalid index

	# Iterate through the list to find all possible averages of three consecutive numbers
	for i in range(len(numbers) - 2):
		# Get the current trio of numbers
		# +3 because it's upper bound exclusive in python
		trio = numbers[i:i + 3]

		# Calculate the average of the trio
		# Also rounding to 3 decimal places
		average = round(sum(trio) / 3,3)

		# Update the minimum average and its index if the current average is lower
		if average < min_average:
			min_average = average
			min_index = i

		# Update the maximum average and its index if the current average is higher
		if average > max_average:
			max_average = average
			max_index = i
	if(debug):
		print(min_average, min_index, max_average, max_index)

	return min_index, min_average, max_index, max_average



def get_hupx_data(requested_date):


	# Define the URL
	#this might change in the future
	url = 'https://hupx.hu/en/dam/homepage/graph.json?date=' + str(requested_date)

	# Define the headers
	headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
	'Accept': '*/*',
	'Accept-Language': 'en-US,en;q=0.5',
	'Accept-Encoding': 'gzip, deflate, br, zstd',
	'Referer': 'https://hupx.hu/en/',
	'Connection': 'keep-alive',
	'Sec-Fetch-Dest': 'empty',
	'Sec-Fetch-Mode': 'no-cors',
	'Sec-Fetch-Site': 'same-origin',
	'X-Requested-With': 'XMLHttpRequest',
	'Priority': 'u=0',
	'Pragma': 'no-cache',
	'Cache-Control': 'no-cache'
}

	# Make the GET request
	response = requests.get(url, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:
		# Print or process the JSON data
		json_data = response.json()
		if(debug):
			print(json_data)
	else:
		print(f"Failed to retrieve data: {response.status_code}")

	columns = [col['label'] for col in json_data['cols']]

	# Create DataFrame
	df = pd.DataFrame(json_data['rows'], columns=columns)

	prices = df.iloc[:, 2].values.tolist()
	if(debug):
		print(prices)
	return prices




def send_data_via_mqtt(ip,username,password,data):



	# MQTT setup
	client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
	client.username_pw_set(username, password)
	client.connect(ip)

	# Send the processed data

	for item in data:
		client.publish(str(item['topic']), str(item['value']))
		if(debug):
			print(item['topic'],item['value'])
	#disconnect
	client.disconnect()




def calculate_dashboard_data(todays_price_list,tomorrows_price_list):


	todays_minimum_price = min(todays_price_list)
	todays_maximum_price = max(todays_price_list)
	todays_minimum_price_hour = todays_price_list.index(min(todays_price_list))
	todays_maximum_price_hour = todays_price_list.index(max(todays_price_list))
	tomorrows_minimum_price = min(tomorrows_price_list)
	tomorrows_maximum_price = max(tomorrows_price_list)
	tomorrows_minimum_price_hour = tomorrows_price_list.index(min(tomorrows_price_list))
	tomorrows_maximum_price_hour = tomorrows_price_list.index(max(tomorrows_price_list))
	current_price = todays_price_list[int(datetime.datetime.now().hour)]
	#get 3 hour block data
	todaysmin3hblockstart, todaysmin3hblockaverage, todaysmax3hblockstart, todaysmax3hblockaverage = avg_extremes_index_of_three(todays_price_list)
	tomorrowsmin3hblockstart, tomorrowsmin3hblockaverage, tomorrowsmax3hblockstart, tomorrowsmax3hblockaverage = avg_extremes_index_of_three(tomorrows_price_list)

	#get the historical data
	historical_data = calculate_historical_data()


	#creating nice timestamps
	todays_minimum_price_hour = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=todays_minimum_price_hour, minute=0, second=0)
	todays_maximum_price_hour = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=todays_maximum_price_hour, minute=0, second=0)
	tomorrows_minimum_price_hour = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=tomorrows_minimum_price_hour, minute=0, second=0)
	tomorrows_maximum_price_hour = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=tomorrows_maximum_price_hour, minute=0, second=0)
	todaysmin3hblockstart = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=todaysmin3hblockstart, minute=0, second=0)
	todaysmax3hblockstart = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=todaysmax3hblockstart, minute=0, second=0)
	tomorrowsmin3hblockstart = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=tomorrowsmin3hblockstart, minute=0, second=0)
	tomorrowsmax3hblockstart = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=tomorrowsmax3hblockstart, minute=0, second=0)


	#if we have the exact same data for both request that means the data is not available yet and the server responded with the latest available data which is todays
	global mqtt_dict
	now = datetime.datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
	if(todays_price_list!=tomorrows_price_list):
		tomorrows_data_available=True


		#creating the mqtt dictionary
		mqtt_dict =[
				#todays data
				{"topic": "/home/hupx/currentprice", "value": current_price},
				{"topic": "/home/hupx/todaysmineuro", "value": todays_minimum_price},
				{"topic": "/home/hupx/todaysminhour", "value": todays_minimum_price_hour},
				{"topic": "/home/hupx/todaysmaxeuro", "value": todays_maximum_price},
				{"topic": "/home/hupx/todaysmaxhour", "value": todays_maximum_price_hour},
				{"topic": "/home/hupx/todaysmin3hblockstart", "value": todaysmin3hblockstart},
				{"topic": "/home/hupx/todaysmin3hblockaverage", "value": todaysmin3hblockaverage},
				{"topic": "/home/hupx/todaysmax3hblockstart", "value": todaysmax3hblockstart},
				{"topic": "/home/hupx/todaysmax3hblockaverage", "value": todaysmax3hblockaverage},

				#tomorrows data
				{"topic": "/home/hupx/tomorrowsmineuro", "value": tomorrows_minimum_price},
				{"topic": "/home/hupx/tomorrowsminhour", "value": tomorrows_minimum_price_hour},
				{"topic": "/home/hupx/tomorrowsmaxeuro", "value": tomorrows_maximum_price},
				{"topic": "/home/hupx/tomorrowsmaxhour", "value": tomorrows_maximum_price_hour},
				{"topic": "/home/hupx/tomorrowsmin3hblockstart", "value": tomorrowsmin3hblockstart},
				{"topic": "/home/hupx/tomorrowsmin3hblockaverage", "value": tomorrowsmin3hblockaverage},
				{"topic": "/home/hupx/tomorrowsmax3hblockstart", "value": tomorrowsmax3hblockstart},
				{"topic": "/home/hupx/tomorrowsmax3hblockaverage", "value": tomorrowsmax3hblockaverage},

				#historical data
				{"topic": "/home/hupx/7daysminprice", "value": historical_data[0]},
				{"topic": "/home/hupx/7daysmindate", "value": historical_data[1]},
				{"topic": "/home/hupx/30daysminprice", "value": historical_data[2]},
				{"topic": "/home/hupx/30daysmindate", "value": historical_data[3]},
				{"topic": "/home/hupx/90daysminprice", "value": historical_data[4]},
				{"topic": "/home/hupx/90daysmindate", "value": historical_data[5]},

				{"topic": "/home/hupx/7daysmaxprice", "value": historical_data[6]},
				{"topic": "/home/hupx/7daysmaxdate", "value": historical_data[7]},
				{"topic": "/home/hupx/30daysmaxprice", "value": historical_data[8]},
				{"topic": "/home/hupx/30daysmaxdate", "value": historical_data[9]},
				{"topic": "/home/hupx/90daysmaxprice", "value": historical_data[10]},
				{"topic": "/home/hupx/90daysmaxdate", "value": historical_data[11]},

				#update
				{"topic": "/home/hupx/update", "value": str(now)},

			]

		if(debug):
			print(mqtt_dict)

	else:
		tomorrows_data_available=False
		#creating the mqtt dictionary leaving out tomorrows data, so it will go stale in the mqtt broker triggering it to be unavailable
		mqtt_dict =[

				#todays data
				{"topic": "/home/hupx/currentprice", "value": current_price},
				{"topic": "/home/hupx/todaysmineuro", "value": todays_minimum_price},
				{"topic": "/home/hupx/todaysminhour", "value": todays_minimum_price_hour},
				{"topic": "/home/hupx/todaysmaxeuro", "value": todays_maximum_price},
				{"topic": "/home/hupx/todaysmaxhour", "value": todays_maximum_price_hour},
				{"topic": "/home/hupx/todaysmin3hblockstart", "value": todaysmin3hblockstart},
				{"topic": "/home/hupx/todaysmin3hblockaverage", "value": todaysmin3hblockaverage},
				{"topic": "/home/hupx/todaysmax3hblockstart", "value": todaysmax3hblockstart},
				{"topic": "/home/hupx/todaysmax3hblockaverage", "value": todaysmax3hblockaverage},

				#historical data
				{"topic": "/home/hupx/7daysminprice", "value": historical_data[0]},
				{"topic": "/home/hupx/7daysmindate", "value": historical_data[1]},
				{"topic": "/home/hupx/30daysminprice", "value": historical_data[2]},
				{"topic": "/home/hupx/30daysmindate", "value": historical_data[3]},
				{"topic": "/home/hupx/90daysminprice", "value": historical_data[4]},
				{"topic": "/home/hupx/90daysmindate", "value": historical_data[5]},

				{"topic": "/home/hupx/7daysmaxprice", "value": historical_data[6]},
				{"topic": "/home/hupx/7daysmaxdate", "value": historical_data[7]},
				{"topic": "/home/hupx/30daysmaxprice", "value": historical_data[8]},
				{"topic": "/home/hupx/30daysmaxdate", "value": historical_data[9]},
				{"topic": "/home/hupx/90daysmaxprice", "value": historical_data[10]},
				{"topic": "/home/hupx/90daysmaxdate", "value": historical_data[11]},

				#update
				{"topic": "/home/hupx/update", "value": str(now)},


			]






def calculate_historical_data():
	weekly_min_price = float('inf')
	monthly_min_price = float('inf')
	quarterly_min_price = float('inf')

	weekly_max_price = float('-inf')
	monthly_max_price = float('-inf')
	quarterly_max_price = float('-inf')

	#hupx now allowing only 30 days back, might change inh the future if so just adjust the range
	for i in range(1, 30):
		prices = get_hupx_data(date.today()-timedelta(days=i))
		lowest_price = min(prices)
		highest_price = max(prices)

		if(lowest_price<=weekly_min_price) and i<8:
			weekly_min_price = lowest_price
			weekly_min_price_date = str(date.today()-timedelta(days=i))

		if(lowest_price<=monthly_min_price) and i<30:
			monthly_min_price = lowest_price
			monthly_min_price_date = str(date.today()-timedelta(days=i))

		if(lowest_price<=quarterly_min_price) and i<90:
			quarterly_min_price = lowest_price
			quarterly_min_price_date = str(date.today()-timedelta(days=i))

		if(highest_price>=weekly_max_price) and i<8:
			weekly_max_price = highest_price
			weekly_max_price_date = str(date.today()-timedelta(days=i))

		if(highest_price>=monthly_max_price) and i<30:
			monthly_max_price = highest_price
			monthly_max_price_date = str(date.today()-timedelta(days=i))

		if(highest_price>=quarterly_max_price) and i<90:
			quarterly_max_price = highest_price
			quarterly_max_price_date = str(date.today()-timedelta(days=i))


	return (weekly_min_price,
		weekly_min_price_date,
		monthly_min_price,
		monthly_min_price_date,
		quarterly_min_price,
		quarterly_min_price_date,
		weekly_max_price,
		weekly_max_price_date,
		monthly_max_price,
		monthly_max_price_date,
		quarterly_max_price,
		quarterly_max_price_date
		)

calculate_dashboard_data(get_hupx_data(today),get_hupx_data(tomorrow))
send_data_via_mqtt(ip,username,password,mqtt_dict)
if(debug):
	print(mqtt_dict)

