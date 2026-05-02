import pandas as pd
from solar import get_solar_hours
import time
from spatial import calculate_transit_distances
from map_output import build_map

#creating a scoring function to assess viabilities of different areas.

def score_parcel(sun_hours, food_desert_score,transit_distance, lot_size):
    score = 0

    score += min(sun_hours/2000,1) * 30   ## capping sun hours here to convert to a 0-1 scale. 
    score += food_desert_score * 25
    score += max(0, 1 - transit_distance/1000) * 20
    score += min(lot_size/10000, 1) * 25  ## capping lot size area to 10000, can alter

    return round(score, 2)


# load in the data
df = pd.read_csv('data/parcels.csv')

#quick inspection
print(df.shape)
print(df.head())
print(df.dtypes)

# Filter to eligible land only
eligible = df[df['land_use'].isin(['vacant', 'open space'])]

print(f"Total parcels: {len(df)}")
print(f"Eligible parcels: {len(eligible)}")
print(eligible[['parcel_id', 'address', 'land_use']])


eligible = eligible.copy()

eligible['score'] = eligible.apply(lambda row: score_parcel(
    row['sun_hours'],
    row['food_desert_score'],
    row['transit_distance_m'],
    row['lot_sqft']
), axis = 1)


ranked = eligible.sort_values('score',ascending=False)

print(ranked)

print("\n--- FETCHING REAL SOLAR DATA ---")

for idx, row in eligible.iterrows():
    real_solar = get_solar_hours(row['lat'], row['lon']) #passed in the synthetic data by row into the function built
    eligible.at[idx, 'sun_hours'] = real_solar
    print(f"Parcel {row['parcel_id']} — {row['address']}: {real_solar:.1f} kWh")
    time.sleep(0.5) 


final_ranked = eligible.sort_values('score', ascending=False)
print(final_ranked[['parcel_id', 'address', 'land_use', 'score']])


# calculate real transit distances
print("\n--- CALCULATING REAL TRANSIT DISTANCES ---")
eligible = calculate_transit_distances(eligible)
print(eligible[['parcel_id', 'address', 'transit_distance_m']])

print("\n")

# final re-score with all real data
print("\n--- FINAL RANKING (all real data) ---")

eligible['score'] = eligible.apply(lambda row: score_parcel(
    row['sun_hours'],
    row['food_desert_score'],
    row['transit_distance_m'],
    row['lot_sqft']
), axis=1)

final = eligible.sort_values('score', ascending=False)
print(final[['parcel_id', 'address', 'land_use', 'transit_distance_m', 'score']])


print("\n--- BUILDING MAP ---")
build_map(final)