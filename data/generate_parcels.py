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

df.to_csv('data/parcels.csv', index=False)
print(df)
