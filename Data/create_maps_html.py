import pandas as pd
import folium
from folium import plugins
import json
from pathlib import Path

output_dir = Path(r"C:\Users\aniza\Task 1\Assignment 9")

fields = pd.read_csv('fields.csv')
vegetation = pd.read_csv('vegetation_health.csv')
weather_yield = pd.read_csv('weather_yield_aligned.csv')

def calculate_soil_health_score(row):
    score = 0
    om = row['organic_matter_pct']
    score += 25 if om >= 4.0 else 20 if om >= 3.0 else 15 if om >= 2.0 else 10 if om >= 1.0 else 5
    ph = row['pH']
    score += 20 if 6.0 <= ph <= 7.0 else 15 if 5.5 <= ph <= 7.5 else 10 if 5.0 <= ph <= 8.0 else 5
    cec = row['CEC_meq_100g']
    score += 20 if cec >= 20 else 15 if cec >= 15 else 10 if cec >= 10 else 5
    bd = row['bulk_density_g_cm3']
    score += 15 if bd <= 1.2 else 10 if bd <= 1.4 else 5 if bd <= 1.6 else 2
    awc = row['available_water_capacity_cm']
    score += 10 if awc >= 0.20 else 7 if awc >= 0.15 else 4 if awc >= 0.10 else 2
    ec = row['EC_dS_m']
    score += 10 if ec <= 0.5 else 7 if ec <= 1.0 else 4 if ec <= 1.5 else 2
    return score

fields['soil_health_score'] = fields.apply(calculate_soil_health_score, axis=1)
fields['avg_yield'] = (fields['yield_2023_bu_ac'] + fields['yield_2024_bu_ac'] + fields['yield_2025_bu_ac']) / 3

ndvi_annual = vegetation.groupby(['field_id', 'year'])['ndvi'].mean().reset_index()
ndvi_pivot = ndvi_annual.pivot(index='field_id', columns='year', values='ndvi').reset_index()
ndvi_pivot.columns = ['field_id', 'ndvi_2023', 'ndvi_2024', 'ndvi_2025']
fields = fields.merge(ndvi_pivot, on='field_id', how='left')
fields['avg_ndvi'] = fields[['ndvi_2023', 'ndvi_2024', 'ndvi_2025']].mean(axis=1)

weather_annual = weather_yield.groupby('field_id')['annual_precip_mm'].mean().reset_index()
weather_annual.columns = ['field_id', 'avg_precip']
fields = fields.merge(weather_annual, on='field_id', how='left')

center_lat = fields['latitude'].mean()
center_lon = fields['longitude'].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='cartodbpositron')

folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(m)
folium.TileLayer('cartodbdark_matter', name='Dark Map').add_to(m)

health_layer = folium.FeatureGroup(name='Soil Health Score')
for _, row in fields.iterrows():
    color = '#2E7D32' if row['soil_health_score'] >= 80 else '#66BB6A' if row['soil_health_score'] >= 60 else '#FF9800' if row['soil_health_score'] >= 40 else '#D32F2F'
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=row['field_acres'] / 30,
        color='black',
        weight=1,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(f"""
            <b>{row['field_name']}</b> ({row['field_id']})<br>
            <b>Soil Health Score:</b> {row['soil_health_score']}<br>
            <b>Commodity:</b> {row['commodity_2023']}<br>
            <b>Acres:</b> {row['field_acres']}<br>
            <b>OM:</b> {row['organic_matter_pct']}%<br>
            <b>pH:</b> {row['pH']}<br>
            <b>CEC:</b> {row['CEC_meq_100g']}<br>
            <b>Drainage:</b> {row['drainage_class']}
        """, max_width=250)
    ).add_to(health_layer)
health_layer.add_to(m)

yield_layer = folium.FeatureGroup(name='Yield (bu/ac)')
for _, row in fields.iterrows():
    yield_val = row['avg_yield']
    color = '#1A237E' if yield_val >= 200 else '#1565C0' if yield_val >= 150 else '#42A5F5' if yield_val >= 100 else '#90CAF9' if yield_val >= 50 else '#FFECB3'
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=row['field_acres'] / 30,
        color='black',
        weight=1,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(f"""
            <b>{row['field_name']}</b> ({row['field_id']})<br>
            <b>Avg Yield:</b> {yield_val:.1f} bu/ac<br>
            <b>Yield 2023:</b> {row['yield_2023_bu_ac']}<br>
            <b>Yield 2024:</b> {row['yield_2024_bu_ac']}<br>
            <b>Yield 2025:</b> {row['yield_2025_bu_ac']}<br>
            <b>Commodity:</b> {row['commodity_2023']}<br>
            <b>Acres:</b> {row['field_acres']}
        """, max_width=250)
    ).add_to(yield_layer)
yield_layer.add_to(m)

ndvi_layer = folium.FeatureGroup(name='Vegetation Health (NDVI)')
for _, row in fields.iterrows():
    ndvi = row['avg_ndvi']
    color = '#1B5E20' if ndvi >= 0.7 else '#388E3C' if ndvi >= 0.5 else '#7CB342' if ndvi >= 0.3 else '#FFA000' if ndvi >= 0.2 else '#D32F2F'
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=row['field_acres'] / 30,
        color='black',
        weight=1,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(f"""
            <b>{row['field_name']}</b> ({row['field_id']})<br>
            <b>Avg NDVI:</b> {ndvi:.3f}<br>
            <b>NDVI 2023:</b> {row['ndvi_2023']:.3f}<br>
            <b>NDVI 2024:</b> {row['ndvi_2024']:.3f}<br>
            <b>NDVI 2025:</b> {row['ndvi_2025']:.3f}<br>
            <b>Commodity:</b> {row['commodity_2023']}<br>
            <b>Avg Precip:</b> {row['avg_precip']:.1f} mm
        """, max_width=250)
    ).add_to(ndvi_layer)
ndvi_layer.add_to(m)

drainage_layer = folium.FeatureGroup(name='Drainage Class')
drain_colors = {'Very Poor': '#1565C0', 'Poor': '#42A5F5', 'Somewhat Poor': '#90CAF9', 'Moderately Well': '#81C784', 'Well': '#2E7D32'}
for _, row in fields.iterrows():
    color = drain_colors.get(row['drainage_class'], 'gray')
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=row['field_acres'] / 30,
        color='black',
        weight=1,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(f"""
            <b>{row['field_name']}</b> ({row['field_id']})<br>
            <b>Drainage:</b> {row['drainage_class']}<br>
            <b>K Factor:</b> {row['k_factor']}<br>
            <b>Slope:</b> {row['slope_pct']}%<br>
            <b>AWC:</b> {row['available_water_capacity_cm']}<br>
            <b>Bulk Density:</b> {row['bulk_density_g_cm3']}<br>
            <b>EC:</b> {row['EC_dS_m']}
        """, max_width=250)
    ).add_to(drainage_layer)
drainage_layer.add_to(m)

folium.LayerControl().add_to(m)

legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
     padding: 15px; border-radius: 5px; border: 2px solid gray; font-size: 12px;">
     <b>Field Dashboard Legend</b><br><br>
     <b>Size:</b> Field Acres<br><br>
     <b>Color Layers:</b><br>
     <i style="background:#2E7D32;width:12px;height:12px;display:inline-block;"></i> Excellent Health / High Yield / High NDVI<br>
     <i style="background:#66BB6A;width:12px;height:12px;display:inline-block;"></i> Good Health<br>
     <i style="background:#FF9800;width:12px;height:12px;display:inline-block;"></i> Fair Health / Medium Yield<br>
     <i style="background:#D32F2F;width:12px;height:12px;display:inline-block;"></i> Poor Health / Low Yield
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

title_html = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; 
     background-color: white; padding: 10px 20px; border-radius: 5px; border: 2px solid gray;
     font-size: 18px; font-weight: bold;">
     Field Dashboard - Iowa Agricultural Fields (200 Fields)
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

m.save('dashboard_maps.html')

print(f"Saved: dashboard_maps.html")
print(f"Location: {output_dir / 'dashboard_maps.html'}")
print(f"\nLayers available:")
print("  - Soil Health Score")
print("  - Yield (bu/ac)")
print("  - Vegetation Health (NDVI)")
print("  - Drainage Class")
print(f"\nTotal fields: {len(fields)}")
print(f"Center: ({center_lat:.4f}, {center_lon:.4f})")