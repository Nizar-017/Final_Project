import pandas as pd
import numpy as np
from datetime import datetime

np.random.seed(42)

output_dir = r"C:\Users\aniza\Task 1\Assignment 9"

df = pd.read_csv('fields.csv')
unique_locs = df[['latitude', 'longitude']].drop_duplicates().reset_index(drop=True)

print(f"Generating weather data for {len(unique_locs)} locations (2023-2025)...")

all_data = []

base_temp = {
    'Jan': -2, 'Feb': 0, 'Mar': 7, 'Apr': 13, 'May': 18, 'Jun': 23,
    'Jul': 26, 'Aug': 25, 'Sep': 20, 'Oct': 13, 'Nov': 6, 'Dec': 0
}

for year in [2023, 2024, 2025]:
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='D')
    
    for loc_idx, row in unique_locs.iterrows():
        lat, lon = row['latitude'], row['longitude']
        
        lat_factor = (lat - 41.77) / 0.3
        lon_factor = (lon + 93.75) / 0.3
        
        year_variation = (year - 2024) * np.random.uniform(-1, 1)
        
        for date in date_range:
            month = date.strftime('%b')
            base_t = base_temp[month] + year_variation
            
            temp_mean = base_t + np.random.normal(0, 3) + lat_factor * 2
            temp_max = temp_mean + np.random.uniform(5, 12)
            temp_min = temp_mean - np.random.uniform(5, 12)
            
            if month in ['May', 'Jun', 'Jul', 'Aug']:
                precip_prob = 0.35
                precip_base = 4.5
            elif month in ['Mar', 'Apr', 'Sep', 'Oct']:
                precip_prob = 0.25
                precip_base = 2.5
            else:
                precip_prob = 0.2
                precip_base = 1.5
            
            precip = np.random.exponential(precip_base) if np.random.random() < precip_prob else 0
            
            rh = np.random.uniform(45, 85) + (precip > 0) * 15
            rh = min(100, rh)
            
            ws = np.random.uniform(2, 8) + (temp_mean > 20) * 2
            
            all_data.append({
                'latitude': lat,
                'longitude': lon,
                'date': date.strftime('%Y-%m-%d'),
                'year': year,
                'month': date.month,
                'temperature_max_c': round(float(temp_max), 1),
                'temperature_min_c': round(float(temp_min), 1),
                'temperature_mean_c': round(float(temp_mean), 1),
                'precipitation_mm': round(float(precip), 1),
                'relative_humidity_pct': round(float(rh), 1),
                'wind_speed_m_s': round(float(ws), 1)
            })
    
    print(f"  Generated year {year}...")

weather_df = pd.DataFrame(all_data)

weather_df.to_csv(output_dir + '\\weather_data.csv', index=False)

print(f"\nDone! Saved to {output_dir}\\weather_data.csv")
print(f"Total records: {len(weather_df)}")
print(f"Years: {sorted(weather_df['year'].unique())}")
print(f"\nSample:")
print(weather_df.head(10).to_string())