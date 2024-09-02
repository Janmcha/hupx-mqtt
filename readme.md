HUPX Electricity Data Scraper and Home Assistant config file

This repository contains a Python script designed to scrape data from HUPX (Hungarian Electricity Exchange) website. The script retrieves day-ahead electricity market prices and historical data from the past 90 days. It then calculates key statistics such as the minimum and maximum prices, along with the dates of the highest and lowest prices over various time increments (7, 30, and 90 days). This can also be customized I just think these make the most sense idk...

The script also integrates with MQTT to publish the scraped data to an MQTT broker. Additionally, a compatible Home Assistant config.yaml is provided to utilize this data within Home Assistant, including creating relative timestamps to be used in  a dashboard.

![image](https://github.com/user-attachments/assets/6455e6a4-63ac-4dfe-9691-f3c0d6291cb9)


Prerequisites

    Python 3.x
    requests, paho-mqtt, pandas
    MQTT broker (e.g., Mosquitto)
    Home Assistant (optional)

Installation

Clone the Repository

    git clone https://github.com/Janmcha/hupx-mqtt

Edit your hupx.py file with your mqtt broker's data
Edit the following in your config:

    ip = "10.36.4.6"
    username = "mqtt"
    password = "mqtt"

Edit your topics in calculate_dashboard_data() if you are not using the provided yaml config:

    like:
    {"topic": "/home/hupx/currentprice", "value": current_price},




Install Required Python Packages

    sudo apt-get install python3-pip
    pip3 install requests paho-mqtt pandas

Home Assistant Integration

    Edit your configuration.yaml based on the one provided to create sensors and sensors for relative timestamps.
    Restart Home Assistant.
    Set up a cronjob for the data to be updated, once an hour should be more than enough

License : For now let's just got with SSPL because I am petty like that.

Acknowledgments:

    HUPX for asking such an outrageous price that I made this out of spite.
    Home Assistant for its powerful home automation platform.
    The Armbian community for their help when I got stuck.
    My failing sanity for spamming the commit log with fixing typos one by one... 
