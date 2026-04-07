import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import seaborn as sns
import json
from pathlib import Path

output_dir = Path(r"C:\Users\aniza\Task 1\Assignment 9")
output_dir.mkdir(exist_ok=True)

fields = pd.read_csv('fields.csv')
weather = pd.read_csv('weather_data.csv')
weather_yield = pd.read_csv('weather_yield_aligned.csv')
vegetation = pd.read_csv('vegetation_health.csv')

fields['avg_yield'] = (fields['yield_2023_bu_ac'] + fields['yield_2024_bu_ac'] + fields['yield_2025_bu_ac']) / 3

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

def calculate_erosion_risk(row):
    val = row['k_factor'] * row['slope_pct']
    levels = ['Very Low', 'Low', 'Moderate', 'High', 'Very High']
    return levels[0] if val <= 0.1 else levels[1] if val <= 0.3 else levels[2] if val <= 0.6 else levels[3] if val <= 1.0 else levels[4]

def calculate_carbon_storage(row):
    bd_factor = 1 - (row['bulk_density_g_cm3'] / 2.65)
    return (row['topsoil_depth_cm'] * row['organic_matter_pct'] * bd_factor) / 100

fields['soil_health_score'] = fields.apply(calculate_soil_health_score, axis=1)
fields['health_rating'] = pd.cut(fields['soil_health_score'], bins=[0, 40, 60, 80, 100], labels=['Poor', 'Fair', 'Good', 'Excellent'])
fields['erosion_risk'] = fields.apply(calculate_erosion_risk, axis=1)
fields['carbon_storage_t_ha'] = fields.apply(calculate_carbon_storage, axis=1)

vegetation_annual = vegetation.groupby(['field_id', 'year'])['ndvi'].mean().reset_index()
vegetation_pivot = vegetation_annual.pivot(index='field_id', columns='year', values='ndvi').reset_index()
vegetation_pivot.columns = ['field_id', 'ndvi_2023', 'ndvi_2024', 'ndvi_2025']
fields = fields.merge(vegetation_pivot, on='field_id', how='left')
fields['avg_ndvi'] = fields[['ndvi_2023', 'ndvi_2024', 'ndvi_2025']].mean(axis=1)

plt.style.use('seaborn-v0_8-whitegrid')
fig = plt.figure(figsize=(20, 24))
fig.suptitle('FARM DASHBOARD - AT-A-GLANCE CARDS', fontsize=20, fontweight='bold', y=0.98)

gs = gridspec.GridSpec(5, 3, figure=fig, hspace=0.35, wspace=0.25)

colors_h = {'Excellent': '#2E7D32', 'Good': '#66BB6A', 'Fair': '#FF9800', 'Poor': '#D32F2F'}
drain_colors = {'Very Poor': '#1565C0', 'Poor': '#42A5F5', 'Somewhat Poor': '#90CAF9', 'Moderately Well': '#81C784', 'Well': '#2E7D32'}
comm_colors = {'Corn': '#FFD54F', 'Soybeans': '#81C784', 'Wheat': '#8D6E63', 'Algba': '#CE93D8'}

ax1 = fig.add_subplot(gs[0, 0])
scatter = ax1.scatter(fields['longitude'], fields['latitude'], c=fields['soil_health_score'], 
                      cmap='RdYlGn', s=fields['field_acres']/3, alpha=0.7, edgecolors='black', linewidth=0.5)
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Latitude')
ax1.set_title('Card 1: Geospatial Map - Soil Health Score', fontweight='bold')
plt.colorbar(scatter, ax=ax1, label='Health Score')
for _, row in fields.iterrows():
    if row['field_acres'] > 150:
        ax1.annotate(row['field_id'], (row['longitude'], row['latitude']), fontsize=6, alpha=0.7)

ax2 = fig.add_subplot(gs[0, 1])
scatter2 = ax2.scatter(fields['longitude'], fields['latitude'], c=fields['avg_yield'], 
                       cmap='YlOrRd', s=fields['field_acres']/3, alpha=0.7, edgecolors='black', linewidth=0.5)
ax2.set_xlabel('Longitude')
ax2.set_ylabel('Latitude')
ax2.set_title('Card 1: Geospatial Map - Avg Yield (bu/ac)', fontweight='bold')
plt.colorbar(scatter2, ax=ax2, label='Yield')

ax3 = fig.add_subplot(gs[0, 2])
scatter3 = ax3.scatter(fields['longitude'], fields['latitude'], c=fields['avg_ndvi'], 
                       cmap='Greens', s=fields['field_acres']/3, alpha=0.7, edgecolors='black', linewidth=0.5)
ax3.set_xlabel('Longitude')
ax3.set_ylabel('Latitude')
ax3.set_title('Card 1: Geospatial Map - Vegetation Health (NDVI)', fontweight='bold')
plt.colorbar(scatter3, ax=ax3, label='NDVI')

sample_locs = fields[['latitude', 'longitude']].drop_duplicates().head(3)
weather_sample = weather[weather.apply(lambda r: (r['latitude'], r['longitude']) in list(sample_locs.itertuples(index=False)), axis=1)]
weather_sample = weather.merge(sample_locs.assign(key=1), on='latitude').drop('key', axis=1).head(500)

ax4 = fig.add_subplot(gs[1, 0])
weather_sample['date'] = pd.to_datetime(weather_sample['date'])
weather_monthly = weather_sample.groupby(['year', 'month'])['temperature_mean_c'].mean().reset_index()
for year in [2023, 2024, 2025]:
    year_data = weather_monthly[weather_monthly['year'] == year]
    ax4.plot(year_data['month'], year_data['temperature_mean_c'], marker='o', label=str(year), linewidth=2)
ax4.set_xlabel('Month')
ax4.set_ylabel('Temperature (°C)')
ax4.set_title('Card 2: Weather Time Series - Temperature', fontweight='bold')
ax4.legend()
ax4.set_xticks(range(1, 13))

ax5 = fig.add_subplot(gs[1, 1])
weather_monthly_precip = weather_sample.groupby(['year', 'month'])['precipitation_mm'].sum().reset_index()
for year in [2023, 2024, 2025]:
    year_data = weather_monthly_precip[weather_monthly_precip['year'] == year]
    ax5.bar(year_data['month'] + (year-2023)*0.25 - 0.25, year_data['precipitation_mm'], width=0.25, label=str(year), alpha=0.8)
ax5.set_xlabel('Month')
ax5.set_ylabel('Precipitation (mm)')
ax5.set_title('Card 2: Weather Time Series - Precipitation', fontweight='bold')
ax5.legend()
ax5.set_xticks(range(1, 13))

ax6 = fig.add_subplot(gs[1, 2])
weather_yield_grouped = weather_yield.groupby('year')[['avg_temp_c', 'annual_precip_mm']].mean()
x = np.arange(len(weather_yield_grouped))
width = 0.35
bars1 = ax6.bar(x - width/2, weather_yield_grouped['avg_temp_c'], width, label='Avg Temp (°C)', color='#FF5722')
ax6_twin = ax6.twinx()
bars2 = ax6_twin.bar(x + width/2, weather_yield_grouped['annual_precip_mm'], width, label='Precip (mm)', color='#2196F3')
ax6.set_xlabel('Year')
ax6.set_ylabel('Temperature (°C)', color='#FF5722')
ax6_twin.set_ylabel('Precipitation (mm)', color='#2196F3')
ax6.set_title('Card 2: Weather vs Yield Relationship', fontweight='bold')
ax6.set_xticks(x)
ax6.set_xticklabels(weather_yield_grouped.index)
ax6.legend(loc='upper left')
ax6_twin.legend(loc='upper right')

ax7 = fig.add_subplot(gs[2, 0])
health_counts = fields['health_rating'].value_counts()
colors = [colors_h[r] for r in health_counts.index]
ax7.pie(health_counts, labels=[f"{l}\n({c})" for l, c in zip(health_counts.index, health_counts.values)], 
        autopct='', colors=colors, startangle=90)
ax7.set_title('Card 3: Soil Health Metrics - Rating Distribution', fontweight='bold')

ax8 = fig.add_subplot(gs[2, 1])
soil_metrics = ['organic_matter_pct', 'pH', 'CEC_meq_100g', 'topsoil_depth_cm']
soil_means = [fields[m].mean() for m in soil_metrics]
soil_stds = [fields[m].std() for m in soil_metrics]
x_pos = np.arange(len(soil_metrics))
ax8.bar(x_pos, soil_means, yerr=soil_stds, capsize=5, color=['#4CAF50', '#2196F3', '#9C27B0', '#FF9800'], alpha=0.8)
ax8.set_xticks(x_pos)
ax8.set_xticklabels(['OM (%)', 'pH', 'CEC\n(meq/100g)', 'Topsoil\n(cm)'])
ax8.set_ylabel('Value')
ax8.set_title('Card 3: Soil Health Metrics - Key Indicators', fontweight='bold')

ax9 = fig.add_subplot(gs[2, 2])
erosion_counts = fields['erosion_risk'].value_counts()
erosion_colors = {'Very Low': '#2E7D32', 'Low': '#66BB6A', 'Moderate': '#FFC107', 'High': '#FF9800', 'Very High': '#D32F2F'}
ax9.barh(erosion_counts.index, erosion_counts.values, color=[erosion_colors[e] for e in erosion_counts.index])
ax9.set_xlabel('Number of Fields')
ax9.set_title('Card 3: Soil Health Metrics - Erosion Risk', fontweight='bold')

ax10 = fig.add_subplot(gs[3, 0])
ndvi_by_comm = vegetation.groupby('commodity')['ndvi'].mean().sort_values(ascending=True)
colors_ndvi = ['#2E7D32' if v > 0.6 else '#66BB6A' if v > 0.4 else '#FFC107' if v > 0.2 else '#D32F2F' for v in ndvi_by_comm.values]
ax10.barh(ndvi_by_comm.index, ndvi_by_comm.values, color=colors_ndvi)
ax10.set_xlabel('Mean NDVI')
ax10.set_title('Card 4: Vegetation Health by Commodity', fontweight='bold')
ax10.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5, label='Good threshold')

ax11 = fig.add_subplot(gs[3, 1])
ndvi_yearly = vegetation.groupby('year')['ndvi'].mean()
ax11.plot(ndvi_yearly.index, ndvi_yearly.values, marker='o', linewidth=3, markersize=10, color='#2E7D32')
ax11.fill_between(ndvi_yearly.index, ndvi_yearly.values, alpha=0.3, color='#2E7D32')
ax11.set_xlabel('Year')
ax11.set_ylabel('Mean NDVI')
ax11.set_title('Card 4: Vegetation Health - Annual Trend', fontweight='bold')
ax11.set_xticks([2023, 2024, 2025])

ax12 = fig.add_subplot(gs[3, 2])
vegetation_pivot_melt = vegetation.melt(id_vars=['field_id', 'month'], value_vars=['ndvi'], 
                                        var_name='metric', value_name='value')
ndvi_seasonal = vegetation.groupby('month')['ndvi'].mean()
colors_seasonal = ['#BBDEFB' if m in [1,2,12] else '#C8E6C9' if m in [3,4,5] else '#81C784' if m in [6,7,8] else '#FFECB3' if m in [9,10] else '#BBDEFB' for m in ndvi_seasonal.index]
ax12.bar(ndvi_seasonal.index, ndvi_seasonal.values, color=colors_seasonal)
ax12.set_xlabel('Month')
ax12.set_ylabel('Mean NDVI')
ax12.set_title('Card 4: Vegetation Health - Seasonal Pattern', fontweight='bold')
ax12.set_xticks(range(1, 13))

ax13 = fig.add_subplot(gs[4, 0])
corr_cols = ['soil_health_score', 'avg_yield', 'avg_ndvi', 'carbon_storage_t_ha', 'annual_precip_mm' if 'annual_precip_mm' in weather_yield.columns else 'avg_temp_c']
corr_data = fields[['field_id', 'soil_health_score', 'avg_yield', 'avg_ndvi', 'carbon_storage_t_ha']].copy()
weather_annual = weather_yield.groupby('field_id')['annual_precip_mm'].mean().reset_index()
corr_data = corr_data.merge(weather_annual, on='field_id', how='left')
corr_matrix = corr_data.drop('field_id', axis=1).dropna().corr()
sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn', center=0, ax=ax13, fmt='.2f', 
            square=True, linewidths=0.5, cbar_kws={'shrink': 0.8})
ax13.set_title('Card 5: EDA - Correlation Matrix', fontweight='bold')

ax14 = fig.add_subplot(gs[4, 1])
scatter_eda = ax14.scatter(fields['soil_health_score'], fields['avg_yield'], 
                           c=fields['avg_ndvi'], cmap='Greens', s=60, alpha=0.7, edgecolors='black')
ax14.set_xlabel('Soil Health Score')
ax14.set_ylabel('Avg Yield (bu/ac)')
ax14.set_title('Card 5: EDA - Soil Health vs Yield', fontweight='bold')
plt.colorbar(scatter_eda, ax=ax14, label='NDVI')

ax15 = fig.add_subplot(gs[4, 2])
for comm in fields['commodity_2023'].unique():
    comm_data = fields[fields['commodity_2023'] == comm]
    ax15.scatter(comm_data['organic_matter_pct'], comm_data['avg_yield'], 
                 label=comm, s=60, alpha=0.7, edgecolors='black')
ax15.set_xlabel('Organic Matter (%)')
ax15.set_ylabel('Avg Yield (bu/ac)')
ax15.set_title('Card 5: EDA - OM vs Yield by Commodity', fontweight='bold')
ax15.legend()

plt.savefig('dashboard_cards.png', dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig('dashboard_cards.pdf', bbox_inches='tight', facecolor='white', edgecolor='none')

print("=" * 60)
print("DASHBOARD COMPLETE")
print("=" * 60)
print("\nCards Generated:")
print("  1. Geospatial Maps - Soil Health, Yield, NDVI")
print("  2. Weather Time Series - Temp, Precip, Yield Rel")
print("  3. Soil Health Metrics - Rating, Indicators, Erosion")
print("  4. Vegetation Health - By Commodity, Trend, Seasonal")
print("  5. EDA Plots - Correlation, Scatter, OM vs Yield")
print(f"\nOutput Files:")
print(f"  - {output_dir / 'dashboard_cards.png'}")
print(f"  - {output_dir / 'dashboard_cards.pdf'}")
print("\nData Summary:")
print(f"  Fields: {len(fields)}")
print(f"  Avg Soil Health Score: {fields['soil_health_score'].mean():.1f}")
print(f"  Avg Yield: {fields['avg_yield'].mean():.1f} bu/ac")
print(f"  Avg NDVI: {fields['avg_ndvi'].mean():.3f}")