import pandas as pd
import numpy as np
from pathlib import Path
import json

np.random.seed(42)

output_dir = Path(r"C:\Users\aniza\Task 1\Assignment 9")
fields = pd.read_csv('fields.csv')

base_ndvi = {
    'Corn': {'peak': 0.85, 'base': 0.15, 'growing_start': 5, 'growing_end': 9},
    'Soybeans': {'peak': 0.80, 'base': 0.20, 'growing_start': 6, 'growing_end': 9},
    'Wheat': {'peak': 0.75, 'base': 0.25, 'growing_start': 3, 'growing_end': 7},
    'Alfalfa': {'peak': 0.90, 'base': 0.30, 'growing_start': 4, 'growing_end': 9}
}

data_dir = output_dir / 'satellite_bands'
data_dir.mkdir(exist_ok=True)

all_data = []

for year in [2023, 2024, 2025]:
    for _, row in fields.iterrows():
        field_id = row['field_id']
        commodity = row['commodity_2023']
        lat = row['latitude']
        lon = row['longitude']
        
        params = base_ndvi[commodity]
        lat_factor = (lat - 41.9) / 0.15
        year_var = (year - 2024) * np.random.uniform(-0.05, 0.05)
        
        for month in [5, 6, 7, 8]:
            progress = (month - params['growing_start']) / (params['growing_end'] - params['growing_start'])
            if month < params['growing_start'] or month > params['growing_end']:
                ndvi = params['base'] + np.random.uniform(-0.05, 0.05)
            elif progress < 0.5:
                ndvi = params['base'] + (params['peak'] - params['base']) * (progress * 2) + np.random.uniform(-0.05, 0.05)
            else:
                ndvi = params['peak'] - (params['peak'] - params['base']) * ((progress - 0.5) * 2) + np.random.uniform(-0.05, 0.05)
            
            ndvi = ndvi + lat_factor * 0.02 + year_var
            ndvi = max(0.1, min(0.9, ndvi))
            
            red = 0.1 + (1 - ndvi) * 0.3 + np.random.uniform(-0.02, 0.02)
            nir = 0.2 + ndvi * 0.5 + np.random.uniform(-0.02, 0.02)
            swir = 0.05 + (1 - ndvi) * 0.15 + np.random.uniform(-0.01, 0.01)
            blue = 0.15 + np.random.uniform(-0.02, 0.02)
            
            all_data.append({
                'field_id': field_id,
                'commodity': commodity,
                'year': year,
                'month': month,
                'ndvi': round(ndvi, 3),
                'red_reflectance': round(red, 3),
                'nir_reflectance': round(nir, 3),
                'swir_reflectance': round(swir, 3),
                'blue_reflectance': round(blue, 3),
                'vegetation_health': 'Excellent' if ndvi >= 0.7 else 'Good' if ndvi >= 0.5 else 'Fair' if ndvi >= 0.3 else 'Poor'
            })

ndvi_df = pd.DataFrame(all_data)
ndvi_df.to_csv('vegetation_health.csv', index=False)

print(f"Saved: vegetation_health.csv")
print(f"Total records: {len(ndvi_df)}")

geojson_features = []
for _, row in fields.iterrows():
    feature = {
        'type': 'Feature',
        'properties': {
            'field_id': row['field_id'],
            'field_name': row['field_name'],
            'commodity': row['commodity_2023'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'area_acres': row['field_acres']
        },
        'geometry': None
    }
    geojson_features.append(feature)

for feature in geojson_features:
    field_data = ndvi_df[ndvi_df['field_id'] == feature['properties']['field_id']]
    feature['properties']['mean_ndvi'] = round(field_data['ndvi'].mean(), 3)
    feature['properties']['ndvi_2023'] = round(field_data[field_data['year'] == 2023]['ndvi'].mean(), 3)
    feature['properties']['ndvi_2024'] = round(field_data[field_data['year'] == 2024]['ndvi'].mean(), 3)
    feature['properties']['ndvi_2025'] = round(field_data[field_data['year'] == 2025]['ndvi'].mean(), 3)

with open('fields_ndvi.geojson', 'w') as f:
    json.dump({'type': 'FeatureCollection', 'features': geojson_features}, f, indent=2)

print(f"Saved: fields_ndvi.geojson")

print(f"\nNDVI by commodity (growing season mean):")
print(ndvi_df.groupby('commodity')['ndvi'].mean().round(3))
print(f"\nSample:")
print(ndvi_df.head(15).to_string())