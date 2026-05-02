import numpy as np
import pandas as pd

np.random.seed(42)

streets = [
    'Market St', 'Park Ave', 'Harbor Dr', 'Industrial Blvd', 'Mission Rd',
    'Broadway', 'El Cajon Blvd', 'University Ave', 'Imperial Ave', 'National City Blvd',
    'Logan Ave', 'Newton Ave', 'Euclid Ave', 'Ocean View Blvd', 'Cesar Chavez Pkwy',
    'Main St', 'Palm Ave', 'Highland Ave', 'Division St', 'Commercial St'
]

land_uses = np.random.choice(
    ['vacant', 'open space', 'commercial', 'industrial'],
    size=20
)

df = pd.DataFrame({
    'parcel_id': np.arange(1001, 1021),
    'address': [f'{np.random.randint(100, 999)} {s}' for s in streets],
    'land_use': land_uses,
    'lot_sqft': np.random.randint(2000, 20000, size=20),
    'sun_hours': np.round(np.random.uniform(1200, 2400, size=20), 1),
    'food_desert_score': np.round(np.random.uniform(0.1, 1.0, size=20), 2),
    'transit_distance_m': np.random.randint(50, 1500, size=20)
})

# Add these after you define the DataFrame -- synthetic data of coordinates
lats = [32.714, 32.748, 32.735, 32.702, 32.721,
        32.756, 32.744, 32.698, 32.731, 32.715,
        32.708, 32.742, 32.751, 32.719, 32.736,
        32.703, 32.728, 32.745, 32.711, 32.759]

lons = [-117.156, -117.132, -117.148, -117.163, -117.141,
        -117.127, -117.155, -117.138, -117.152, -117.144,
        -117.161, -117.129, -117.143, -117.157, -117.136,
        -117.149, -117.133, -117.158, -117.146, -117.131]

df['lat'] = lats
df['lon'] = lons


df['farm_type'] = np.where(
    df['land_use'].isin(['vacant','open space']),
    'ground',
    'rooftop'
)

df['roof_height'] = np.where(
    df['land_use'].isin(['vacant','open space']),
    0,
    np.random.randint(5, 30, size=20)
)

df.to_csv('data/parcels.csv', index=False)


