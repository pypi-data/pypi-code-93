"""
Weather forecasting components with OpenWaetherAPI. 
"""

# Authors: Tolgahan Cepel <tolgahan.cepel@gmail.com>
# License: BSD 3 claus

import requests
import datetime
import dash_bootstrap_components as dbc
import dash_html_components as html

ICON_BASE_URL = "http://openweathermap.org/img/wn/"

class Openwid:
	"""Daily weather forecasting component with OpenWaetherAPI.

	Args:
		api_key (string): unique API key
		latitude (string): latitude of the location
		longitude (string): longitude of the location

	References:
		https://openweathermap.org/api/one-call-api

	"""

	def __init__(self, api_key, latitude, longitude):
		self.api_key = api_key
		self.latitude = latitude
		self.longitude = longitude
		self.forecast_list = []
		self.response_url = "https://api.openweathermap.org/data/2.5/onecall?lat=" + self.latitude + "&lon="+ self.longitude + "&exclude=minutely,hourly&units=metric&appid=" + self.api_key

		response = requests.get(self.response_url)

		for i in range(7):
			self.forecast_list.append(
			[
				response.json()['daily'][i]['weather'][0]['main'],
				str(int(response.json()['daily'][i]['temp']['day'])) + "° "
					+ str(int(response.json()['daily'][i]['temp']['night'])) + "°",
				ICON_BASE_URL + response.json()['daily'][i]['weather'][0]['icon'] + "@4x.png",
				datetime.datetime.fromtimestamp( response.json()['daily'][i]['dt'] ).strftime("%a")
			]
		)

	def get_card(self, city_name, days=4, bg_color="#00202f"):
		""" Weather forecasting boostrap card component.

		Args:
			city_name (string): the city name in card header
			days (int): how many days weather forecast will be shown, default=4
			bg_color (string): background color of the weather card, default=#00202f

		Returns:
			dbc.Card: bootstrap card component that shows weather forecast
		
		"""

		text_style = {"font-size": "calc(0.75em + 0.4vmin)", "text-align": "center", "color": "white"}
		day_style = {"font-size": "calc(0.75em + 0.2vmin)", "text-align": "center", "margin": "0px", "color": "white"}
		header_style = {"font-size": "calc(0.75em + 0.6vmin)", "background": "transparent", "color": "white",
						"border-radius": "10px 10px 0px 0px", "font-weight": "400", "text-align": "center"}
		icon_style = {"height": "calc(3rem - 0.2vmin)", "width":"auto","display": "block", "margin": "0 auto"}

		day_columns_list = []
		
		for i in range(days):
			day_columns_list.append(
				dbc.Col(
					[
						html.P(self.forecast_list[i][3], style=day_style),
						html.Img(src=self.forecast_list[i][2], style=icon_style),
						html.P(self.forecast_list[i][1], style=text_style),
					]
				),
			)

		weather_card = dbc.Card(
			[
				dbc.CardHeader(city_name +  " - " + str(days) + " Day Forecast", style=header_style),
				dbc.CardBody(
					dbc.Row(
						day_columns_list
					), style= {"justify-content": "center", "align-items": "center"}
				)
			], style={"background-color": bg_color, "margin-bottom": "2vh", "border-radius": "10px", "border": "none"}
		)

		return weather_card