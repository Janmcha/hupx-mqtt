import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import paho.mqtt.client as mqtt
import datetime
debug = True

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

	return min_average, min_index, max_average, max_index



def get_hupx_data():

	# Step 1: Fetch the webpage content
	response = requests.get("https://hupx.hu")

	# Step 2: Parse the HTML content
	soup = BeautifulSoup(response.content, "html.parser")


	# Step 3: Find the <script> tag with id="dam-price-graph-data"
	script_tag = soup.find("script", id="dam-price-graph-data")


	# Step 4: Extract the content from the script tag and load it as JSON
	if script_tag:
		# Assuming the script contains just the JSON data without any extra code
		json_data = json.loads(script_tag.string)

		# If there is additional text around the JSON, you'll need to extract the JSON part
		# For example, if the script contains something like "var data = {...};"
		# json_str = script_tag.string.strip().split('=')[-1].strip(' ;')
		# json_data = json.loads(json_str)
		if(debug):
			print(json_data)
	else:
		#they might change the tag in the future 
		print("Script tag with id 'dam-price-graph-data' not found.")

	#getting the date of the latest available data, if it is in the future, then the data for the next day is available by now
	latest_data_date = soup.find("div", class_="flatpickr-wrap")
	if latest_data_date:
		max_date = latest_data_date.get("data-max-date")
		if(debug):
			print(f"Max Date: {max_date}")
	else:
		##they might also change the tag in the future
		print("Div tag with class 'flatpickr-wrap' not found.")


	if (max_date>date.today()):
		next_days_data_available = True
	else:
		next_days_data_available = False
	
	columns = [col['label'] for col in json_data['cols']]

	# Create DataFrame
	df = pd.DataFrame(json_data['rows'], columns=columns)

	if(debug):
	# Display the DataFrame and the latest available data's date
		print(max_date)
		print(df)
		print(next_days_data_available)
	#creating a zero indexed list from the prices 
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
	client.publish("home/sensors/hupxmin", hupxmin)
	client.disconnect()


def create_mqtt_dict();
#creating a dictionary from the data to send in send_data_via_mqtt
	mqtt_dict =[
		{"topic": "/home/hupx/todaysmineuro", "value": 30},
		{"topic": "/home/hupx/todaysminhour", "value": 30},
		{"topic": "/home/hupx/todaysmaxeuro", "value": 30},
		{"topic": "/home/hupx/todaysmaxhour", "value": 30},
		{"topic": "/home/hupx/todaysmin3hblockstart", "value": 30},
		{"topic": "/home/hupx/todaysmax3hblockstart", "value": 30},
		{"topic": "/home/hupx/tomorrowsmineuro", "value": 30},
		{"topic": "/home/hupx/tomorrowsminhour", "value": 30},
		{"topic": "/home/hupx/tomorrowsmaxeuro", "value": 30},
		{"topic": "/home/hupx/tomorrowssmaxhour", "value": 30},
		{"topic": "/home/hupx/tomorrowssmin3hblockstart", "value": 30},
		{"topic": "/home/hupx/tomorrowsmax3hblockstart", "value": 30},
		]




