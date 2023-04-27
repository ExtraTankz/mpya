import requests
from urllib.request import urlretrieve
import json
from datetime import datetime

import PySimpleGUI as sg

sg.theme('DarkTeal10')

API_URL = 'https://api.tomorrow.io/v4/weather/realtime'
with open('API.MPYA', 'r') as f:
    API_KEY = f.readline().strip()
RADAR_OPTIONS = ['National Weather Service', 'Weather Underground']

def get_weather(city, state, zipcode):
    params = {
        'location': f'{city},{state},{zipcode}',
        'units': 'imperial',
        'apikey': API_KEY
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()

def create_weather_str(weather_data):
    tempdir = int(float(weather_data['data']['values']['temperature']))
    humidity = str(weather_data['data']['values']['humidity'])
    precipitation_prob = str(weather_data['data']['values']['precipitationProbability'])
    clothes, reasoning = get_clothing_advice(tempdir)
    return f'Temperature: {tempdir}F\nHumidity: {humidity}%\nPrecipitation Probability: {precipitation_prob}%\nAdvice: Wear {clothes} because it\'s {reasoning}.'

def get_clothing_advice(temp):
    if temp < 20:
        return 'a heavy coat, gloves, scarf, and hat', 'extremely cold (below 20°F)'
    elif temp < 32:
        return 'a heavy coat, gloves, and scarf', 'very cold (20°F - 32°F)'
    elif temp < 45:
        return 'a jacket or coat', 'cold (32°F - 45°F)'
    elif temp < 55:
        return 'a light jacket, hoodie, or sweater', 'cool (45°F - 55°F)'
    elif temp < 65:
        return 'a long-sleeve shirt or light jacket', 'mild (55°F - 65°F)'
    elif temp < 75:
        return 'a t-shirt and shorts, or jeans and a light shirt', 'warm (65°F - 75°F)'
    else:
        return 'light and breathable clothing', 'hot (above 75°F)'

def get_location():
    layout = [
        [sg.Text('Please enter your location information:')],
        [sg.Text('Note: Only one of the boxes are required.')],
        [sg.Text('City:', size=(15, 1)), sg.InputText(key='city')],
        [sg.Text('State:', size=(15, 1)), sg.InputText(key='state')],
        [sg.Text('Zip Code:', size=(15, 1)), sg.InputText(key='zip')],
        [sg.Text('Select radar provider:')],
        [sg.DropDown(RADAR_OPTIONS, key='radar', default_value='National Weather Service')],
        [sg.Submit(), sg.Cancel()]
    ]

    window = sg.Window('Location', layout, resizable = True)

    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Cancel'):
        window.close()
        exit()

    selected_radar = values['radar']
    window.close()
    return values['city'], values['state'], values['zip'], selected_radar

def retrieve_radar_image(selected_radar):
    if selected_radar == 'National Weather Service':
        url = 'https://radar.weather.gov/ridge/standard/CONUS_loop.gif'
    else:
        url = 'https://s.w-x.co/staticmaps/wu/wu/wxtype1200_cur/conus/animate.png'
    urlretrieve(url, 'picture.gif')

def get_current_time():
    now = datetime.now()
    return now.strftime("%A, %B %e, %Y %I:%M %p %Z")

def close_window(event):
    return event == sg.WIN_CLOSED or event == 'OK'

city, state, zipcode, selected_radar = get_location()

try:
    weather_data = get_weather(city, state, zipcode)
except Exception as ex:
    sg.popup_error(f'Unable to retrieve weather data: {ex}')
    exit()

retrieve_radar_image(selected_radar)
weather_str = create_weather_str(weather_data)

layout = [
    [sg.Text('The current date and time is: ')],
    [sg.Text(get_current_time())],
    [sg.Text(weather_str)],
    [sg.Image('picture.gif', key='radar', size=(600, 400))],
    [sg.Button('OK')]
]

window = sg.Window('Weather', layout, icon=('umbrella.ico'), resizable = True)

while True:
    event, _ = window.read(timeout=500)
    window['radar'].UpdateAnimation('picture.gif', time_between_frames=500)
    if close_window(event):
        break

window.close()