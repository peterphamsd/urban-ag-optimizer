import pandas as pd
from spatial import calculate_transit_distances
from map_output import build_map
from monte_carlo import run_simulation

def score_parcel(p_viable, food_desert_score, transit_distance, lot_size):
    score = 0
    score += p_viable * 30
    score += food_desert_score * 25
    score += max(0, 1 - transit_distance / 1000) * 20
    score += min(lot_size / 10000, 1) * 25
    return round(score, 2)

# Load data
df = pd.read_csv('data/parcels.csv')
print(f"Total parcels: {len(df)}")
print(df.dtypes)

# Filter eligible land
eligible = df[df['land_use'].isin(['vacant', 'open space'])].copy()
print(f"Eligible parcels: {len(eligible)}")

# Calculate real transit distances
print("\n--- CALCULATING REAL TRANSIT DISTANCES ---")
eligible = calculate_transit_distances(eligible)
print(eligible[['parcel_id', 'address', 'transit_distance_m']])

# Run Monte Carlo for each eligible parcel
print("\n--- RUNNING MONTE CARLO SIMULATIONS ---")
print("(this will take 2-3 minutes)")

mc_results = {}
for idx, row in eligible.iterrows():
    print(f"Simulating {row['address']}...")
    mc = run_simulation(
        lat=row['lat'],
        lon=row['lon'],
        elevation=row['roof_height'],
        roof_height=row['roof_height'],
        n=1000
    )
    mc_results[row['parcel_id']] = mc

# Add Monte Carlo results to DataFrame
eligible['p_viable']        = eligible['parcel_id'].map(
    lambda x: mc_results[x]['p_viable'])
eligible['avg_cost']        = eligible['parcel_id'].map(
    lambda x: mc_results[x]['avg_irrigation_cost'])
eligible['yield_stability'] = eligible['parcel_id'].map(
    lambda x: mc_results[x]['yield_stability'])

# Score and rank
eligible['score'] = eligible.apply(lambda row: score_parcel(
    row['p_viable'],
    row['food_desert_score'],
    row['transit_distance_m'],
    row['lot_sqft']
), axis=1)

final = eligible.sort_values('score', ascending=False)

print("\n--- FINAL RANKING (Monte Carlo + FAO-56) ---")
print(final[['parcel_id', 'address', 'land_use',
             'p_viable', 'avg_cost', 'yield_stability', 'score']])

# Build map
print("\n--- BUILDING MAP ---")
build_map(final)