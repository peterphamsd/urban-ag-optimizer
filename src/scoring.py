import pandas as pd
from solar import get_solar_hours
import time
from spatial import calculate_transit_distances
from map_output import build_map
from monte_carlo import run_simulation

#creating a scoring function to assess viabilities of different areas.

def score_parcel(p_viable, food_desert_score, transit_distance, lot_size):
    score = 0

    score += p_viable * 30                                      # 30% weight
    score += food_desert_score * 25                             # 25% weight
    score += max(0, 1 - transit_distance / 1000) * 20          # 20% weight
    score += min(lot_size / 10000, 1) * 25                      # 25% weight

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

print("\n--- RUNNING MONTE CARLO SIMULATIONS ---")
print("(this will take 2-3 minutes for all parcels)")

mc_results = {}

for idx, row in eligible.iterrows():
    print(f"Simulating {row['address']}...")
    mc = run_simulation(
        lat=row['lat'],
        lon=row['lon'],
        elevation=row['roof_height'],
        roof_height=row['roof_height'],
        n=1000  # use 1000 for speed, bump to 10000 for final run
    )
    mc_results[row['parcel_id']] = mc

# Add Monte Carlo results to DataFrame
eligible['p_viable']        = eligible['parcel_id'].map(
    lambda x: mc_results[x]['p_viable'])
eligible['avg_cost']        = eligible['parcel_id'].map(
    lambda x: mc_results[x]['avg_irrigation_cost'])
eligible['yield_stability'] = eligible['parcel_id'].map(
    lambda x: mc_results[x]['yield_stability'])


eligible['score'] = eligible.apply(lambda row: score_parcel(
    row['p_viable'],
    row['food_desert_score'],
    row['transit_distance_m'],
    row['lot_sqft']
), axis=1)


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
print("\n--- FINAL RANKING (Monte Carlo + FAO-56) ---")
final = eligible.sort_values('score', ascending=False)
print(final[['parcel_id', 'address', 'land_use', 
             'p_viable', 'avg_cost', 'yield_stability', 'score']])

eligible['score'] = eligible.apply(lambda row: score_parcel(
    row['sun_hours'],
    row['food_desert_score'],
    row['transit_distance_m'],
    row['lot_sqft']
), axis=1)

print("\n--- BUILDING MAP ---")
build_map(final)