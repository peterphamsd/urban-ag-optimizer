import requests
import pandas as pd

def get_weather_data(lat,lon, start_year = 2020, end_year = 2025):
    
    url = 'https://power.larc.nasa.gov/api/temporal/daily/point' #NASA power API

    params = {
        "parameters": "T2M,T2M_MIN,T2M_MAX,WS2M,RH2M,ALLSKY_SFC_SW_DWN,PRECTOTCORR",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": f"{start_year}0101",
        "end": f"{end_year}1231",
        "format": "JSON"
    }

    response = requests.get(url, params=params)  #pass in that parameters
    data = response.json()

    properties = data['properties']['parameter']

    df = pd.DataFrame(properties)
    df.index = pd.to_datetime(df.index, format='%Y%m%d')
    df.columns = ['temp_mean', 'temp_min', 'temp_max', 'wind_speed', 'humidity', 'solar_rad', 'rainfall']

    return df

df = get_weather_data(32.735, -117.148)
print(df.head(10))
print(f"Shape: {df.shape}")

    

