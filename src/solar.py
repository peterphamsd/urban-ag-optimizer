import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv('NREL_API_KEY')

def get_solar_hours(lat, lon):
    url = "https://developer.nlr.gov/api/pvwatts/v6.json"
    
    params = {
        "api_key": API_KEY,
        "lat": lat,
        "lon": lon,
        "system_capacity": 1,
        "azimuth": 180,
        "tilt": 20,
        "array_type": 1,
        "module_type": 1,
        "losses": 14
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data['outputs']['ac_annual']
    except Exception as e:
        print(f"API error for ({lat}, {lon}): {e}")
        return None