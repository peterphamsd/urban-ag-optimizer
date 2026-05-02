import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def get_transit_stops():
    gdf = gpd.read_file('data/transit_stops.geojson')
    print(f"Columns: {gdf.columns.tolist()}")
    print(f"Total stops: {len(gdf)}")
    print(gdf.head())
    
    return gdf

get_transit_stops()