import pandas as pd

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