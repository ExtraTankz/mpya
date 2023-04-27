from geopy.geocoders import Nominatim
import requests
from urllib.request import urlretrieve
import json
from datetime import datetime
import PySimpleGUI as sg
from styles import font, title_color, background_color, pad, button_color
sg.theme('DarkBrown1')
API_URL = 'https://api.tomorrow.io/v4/weather/realtime'

# Use context manager to open the file
with open('API.MPYA', 'r') as f:
    API_KEY = f.readline().strip()
    SRSS_API_KEY = f.readline().strip()

def get_sunrise_sunset(city):
    # create a geolocator object with a custom name for the user agent
    geolocator = Nominatim(user_agent='my-application-1.0')

    # get the latitude and longitude of a city
    location = geolocator.geocode(city)
    latitude = location.latitude
    longitude = location.longitude

    # set the API endpoint URL
    url = f"https://api.ipgeolocation.io/astronomy?apiKey={SRSS_API_KEY}&lat={latitude}&long={longitude}"

    # send the GET request and catch any exceptions that may occur
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as ex1:
        raise Exception(f'Error retrieving sunrise/sunset data.\n{ex1}')

    # extract the sunrise and sunset times from the JSON response
    data = response.json()
    datasr = datetime.strptime(data['sunrise'], "%H:%M")
    datass = datetime.strptime(data['sunset'], "%H:%M")
    sunrise = datasr.strftime("%I:%M %p")
    sunset = datass.strftime("%I:%M %p")

    return sunrise, sunset

def get_weather(city, state, zipcode):
    params = {
        'location': f'{city},{state},{zipcode}',
        'units': 'imperial',
        'apikey': API_KEY
    }

    # send the GET request and catch any exceptions that may occur
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as ex2:
        raise Exception(f'Error retrieving weather data.\n{ex2}')

    return response.json()

def create_weather_str(weather_data):
    temp = round(float(weather_data['data']['values']['temperature']))
    temp_str = f'{temp}°F'
    humidity = str(weather_data['data']['values']['humidity'])
    precipitation_prob = str(weather_data['data']['values']['precipitationProbability'])
    clothes, reasoning = get_clothing_advice(temp)
    return f'Temperature: {temp_str}\nHumidity: {humidity}%\nPrecipitation Probability: {precipitation_prob}%\nAdvice: Wear {clothes} because it\'s {reasoning}.'

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
    location_group = [
        [sg.Text('City:', font=font, size=(15,1)), sg.InputText(key='city', justification='right', font=font, size=(10,1))],
        [sg.Text('State:', font=font, size=(15,1)), sg.InputText(key='state', justification='right', font=font, size=(10,1))],
        [sg.Text('Zip Code:', font=font, size=(15,1)), sg.InputText(key='zip', justification='right', font=font, size=(10,1))],
    ]
    location_layout = [
        [sg.Text('Please enter your location information:', font=font, pad=pad)],
        [sg.Text('Note: For sunrise/sunset data fill in City.', font=font, pad=pad)],
        [sg.Frame('Location', location_group, title_color=title_color, font=font, pad=pad)]
    ]
    
    button_layout = [
        [sg.Radio('Weather Underground', 'radar', default=True, key='wunderground', font=font, pad=pad)],
        [sg.Radio('National Weather Service', 'radar', key='nws', font=font, pad=pad)],
        [sg.Submit('Submit', button_color=button_color, font=font, pad=pad), sg.Button('Cancel', font=font, pad=pad)]
    ]
    
    layout = [
        [sg.Column(location_layout, pad=pad)],
        [sg.Column(button_layout, pad=pad)]
    ]
    
    window = sg.Window('Location', layout, background_color=background_color)
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Cancel'):
        window.close()
        exit()

    if values['nws']:
        selected_radar = 'National Weather Service'
    else:
        selected_radar = 'Weather Underground'

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
    return event in (sg.WIN_CLOSED, 'OK')

# Get location data from user input
city, state, zipcode, selected_radar = get_location()

# Get weather data using user's location
try:
    weather_data = get_weather(city, state, zipcode)
except Exception as err:
    if "429" in str(err):
        sg.popup_error("API Limit reached, Check Tomorrow.io!")
    else:
        sg.popup_error(f'Error: {err}')
    exit()

# Get sunrise and sunset times of the location
if city != '':
    try:
        sunrise, sunset = get_sunrise_sunset(city)
    except Exception as err:
        sg.popup_error(f'Error: {err}')
        exit()
else:
    sunrise, sunset = '', ''

# Create weather string for display
weather_str = create_weather_str(weather_data)

# Get current time for display
current_time = get_current_time()

# Retrieve radar image based on user's selected provider
retrieve_radar_image(selected_radar)

# Display user's input and weather data in a new window
location_parts = []
if city:
    location_parts.append(city)
if state:
    location_parts.append(state)
if zipcode:
    location_parts.append(zipcode)

location = ', '.join(location_parts) if len(location_parts) > 0 else ''

layout = [
    [sg.Column([[sg.Text(f'Weather for {location} as of {current_time}', font=font, text_color='white', pad=pad, size=(None, 1), justification='center')]], element_justification='center', expand_x=True)],
    [sg.Column([[sg.Text(weather_str, font=font, pad=pad, size=(None, 3), justification='center')]], element_justification='center', expand_x=True)],    
    [sg.Frame('', [[sg.Image(filename='picture.gif', key='-IMAGE-', pad=pad, background_color='white')]], border_width=0, pad=pad)],

    [sg.Column([[sg.Button('OK', button_color=button_color, font=font, pad=pad)]], element_justification='center', expand_x=True)],
]

window = sg.Window('Weather', layout, resizable = True, background_color=background_color)

while True:
    event, values = window.read(timeout=150)

    if event in (sg.WIN_CLOSED, 'OK'):
        break
    
    # Update the animation every timeout milliseconds
    window['-IMAGE-'].update_animation('picture.gif', time_between_frames=150)
window.close()