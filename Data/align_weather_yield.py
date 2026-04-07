import pandas as pd

fields = pd.read_csv('fields.csv')
weather = pd.read_csv('weather_data.csv')

weather_annual = weather.groupby(['latitude', 'longitude', 'year']).agg({
    'temperature_mean_c': 'mean',
    'temperature_max_c': 'max',
    'temperature_min_c': 'min',
    'precipitation_mm': 'sum',
    'relative_humidity_pct': 'mean',
    'wind_speed_m_s': 'mean'
}).reset_index()

weather_annual = weather_annual.rename(columns={
    'temperature_mean_c': 'avg_temp_c',
    'temperature_max_c': 'max_temp_c',
    'temperature_min_c': 'min_temp_c',
    'precipitation_mm': 'annual_precip_mm',
    'relative_humidity_pct': 'avg_rh_pct',
    'wind_speed_m_s': 'avg_wind_m_s'
})

field_yields = fields[['field_id', 'field_name', 'commodity_2023', 'yield_2023_bu_ac', 'yield_2024_bu_ac', 'yield_2025_bu_ac', 'field_acres', 'latitude', 'longitude']]

annual_long = pd.melt(
    field_yields,
    id_vars=['field_id', 'field_name', 'commodity_2023', 'field_acres', 'latitude', 'longitude'],
    value_vars=['yield_2023_bu_ac', 'yield_2024_bu_ac', 'yield_2025_bu_ac'],
    var_name='yield_source',
    value_name='yield_bu_ac'
)
annual_long['year'] = annual_long['yield_source'].str.extract(r'(\d+)').astype(int)
annual_long = annual_long.drop('yield_source', axis=1)

merged = annual_long.merge(
    weather_annual,
    on=['latitude', 'longitude', 'year'],
    how='left'
)

merged = merged.drop(['latitude', 'longitude'], axis=1)

merged = merged[['field_id', 'field_name', 'commodity_2023', 'field_acres', 'year', 'yield_bu_ac',
                 'avg_temp_c', 'max_temp_c', 'min_temp_c', 'annual_precip_mm', 'avg_rh_pct', 'avg_wind_m_s']]

merged.to_csv('weather_yield_aligned.csv', index=False)

print("Saved: weather_yield_aligned.csv")
print(f"Total records: {len(merged)}")
print(f"Fields: {merged['field_id'].nunique()}")
print(f"Years: {sorted(merged['year'].unique())}")
print(f"\nYear alignment: Weather and Yield for same year (2023, 2024, 2025)")
print(f"\nSample:")
print(merged.head(10).to_string())