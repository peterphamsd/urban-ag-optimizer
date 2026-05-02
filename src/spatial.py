import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def calculate_transit_distances(eligible_df):
    #load in that transit stop data
    transit = gpd.read_file('data/transit_stops.geojson')

    #convert the eligible parcels to the geodf
    geometry = [Point(row['lon'], row['lat']) for _, row in eligible_df.iterrows()]
    parcels_gdf = gpd.GeoDataFrame(eligible_df, geometry=geometry, crs='EPSG:4326')

    #distance from degree, we want it in meters
    parcels_gdf = parcels_gdf.to_crs(epsg=3857)
    transit = transit.to_crs(epsg=3857)

    #find the nearest transit stop distance to each of our parcel
    parcels_gdf['transit_distance_m'] = parcels_gdf.geometry.apply(
        lambda p: transit.distance(p).min()
    )

    return parcels_gdf

