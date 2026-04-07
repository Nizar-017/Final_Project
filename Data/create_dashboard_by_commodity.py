import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

output_dir = Path(r"C:\Users\aniza\Task 1\Assignment 9")
output_dir.mkdir(exist_ok=True)

fields = pd.read_csv('fields.csv')
weather = pd.read_csv('weather_data.csv')
weather_yield = pd.read_csv('weather_yield_aligned.csv')
vegetation = pd.read_csv('vegetation_health.csv')

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

fields['soil_health_score'] = fields.apply(calculate_soil_health_score, axis=1)
fields['health_rating'] = pd.cut(fields['soil_health_score'], bins=[0, 40, 60, 80, 100], labels=['Poor', 'Fair', 'Good', 'Excellent'])
fields['erosion_risk'] = fields.apply(calculate_erosion_risk, axis=1)
fields['avg_yield'] = (fields['yield_2023_bu_ac'] + fields['yield_2024_bu_ac'] + fields['yield_2025_bu_ac']) / 3

fields['yield_percentile'] = fields.groupby('commodity_2023')['avg_yield'].rank(pct=True) * 100

ndvi_annual = vegetation.groupby(['field_id', 'year'])['ndvi'].mean().reset_index()
ndvi_pivot = ndvi_annual.pivot(index='field_id', columns='year', values='ndvi').reset_index()
ndvi_pivot.columns = ['field_id', 'ndvi_2023', 'ndvi_2024', 'ndvi_2025']
fields = fields.merge(ndvi_pivot, on='field_id', how='left')
fields['avg_ndvi'] = fields[['ndvi_2023', 'ndvi_2024', 'ndvi_2025']].mean(axis=1)

commodities = ['Corn', 'Soybeans', 'Wheat', 'Alfalfa']
comm_colors = {'Corn': '#FFD54F', 'Soybeans': '#81C784', 'Wheat': '#8D6E63', 'Alfalfa': '#CE93D8'}
comm_titles = {'Corn': 'CORN', 'Soybeans': 'SOYBEANS', 'Wheat': 'WHEAT', 'Alfalfa': 'ALFALFA'}

colors_h = {'Excellent': '#2E7D32', 'Good': '#66BB6A', 'Fair': '#FF9800', 'Poor': '#D32F2F'}
drain_colors = {'Very Poor': '#1565C0', 'Poor': '#42A5F5', 'Somewhat Poor': '#90CAF9', 'Moderately Well': '#81C784', 'Well': '#2E7D32'}

fig = plt.figure(figsize=(24, 32))
fig.suptitle('FARM DASHBOARD BY COMMODITY', fontsize=24, fontweight='bold', y=0.99)

gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.35, wspace=0.25)

for idx, comm in enumerate(commodities):
    comm_fields = fields[fields['commodity_2023'] == comm].copy()
    weather_comm = weather_yield[weather_yield['commodity_2023'] == comm].copy()
    veg_comm = vegetation[vegetation['commodity'] == comm].copy()
    
    row_start = idx * 4
    
    ax1 = fig.add_subplot(gs[idx, 0])
    scatter = ax1.scatter(comm_fields['longitude'], comm_fields['latitude'], 
                          c=comm_fields['soil_health_score'], cmap='RdYlGn', 
                          s=comm_fields['field_acres']/2, alpha=0.7, edgecolors='black')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title(f'{comm_titles[comm]}: Soil Health Score', fontweight='bold')
    plt.colorbar(scatter, ax=ax1, label='Score')
    
    ax2 = fig.add_subplot(gs[idx, 1])
    scatter2 = ax2.scatter(comm_fields['longitude'], comm_fields['latitude'], 
                           c=comm_fields['avg_yield'], cmap='YlOrRd', 
                           s=comm_fields['field_acres']/2, alpha=0.7, edgecolors='black')
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.set_title(f'{comm_titles[comm]}: Yield (bu/ac)', fontweight='bold')
    plt.colorbar(scatter2, ax=ax2, label='Yield')
    
    ax3 = fig.add_subplot(gs[idx, 2])
    health_counts = comm_fields['health_rating'].value_counts()
    colors = [colors_h.get(r, 'gray') for r in health_counts.index]
    if len(health_counts) > 0:
        ax3.pie(health_counts, labels=[f"{l}\n({c})" for l, c in zip(health_counts.index, health_counts.values)], 
                autopct='', colors=colors, startangle=90)
    ax3.set_title(f'{comm_titles[comm]}: Health Rating', fontweight='bold')
    
    ax4 = fig.add_subplot(gs[idx, 3])
    if len(comm_fields) > 0:
        ax4.scatter(comm_fields['soil_health_score'], comm_fields['avg_yield'], 
                    c=comm_fields['avg_ndvi'], cmap='Greens', s=60, alpha=0.7, edgecolors='black')
    ax4.set_xlabel('Soil Health Score')
    ax4.set_ylabel('Yield (bu/ac)')
    ax4.set_title(f'{comm_titles[comm]}: Health vs Yield', fontweight='bold')

plt.savefig('dashboard_by_commodity.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.savefig('dashboard_by_commodity.pdf', bbox_inches='tight', facecolor='white')

print("=" * 70)
print("DASHBOARD BY COMMODITY COMPLETE")
print("=" * 70)
print("\nSeparated dashboards for each commodity:")
for comm in commodities:
    c = fields[fields['commodity_2023'] == comm]
    corr = c['soil_health_score'].corr(c['avg_yield'])
    avg_yield = c['avg_yield'].mean()
    avg_health = c['soil_health_score'].mean()
    pct_80 = (c['yield_percentile'] >= 80).sum()
    print(f"\n{comm}:")
    print(f"  Fields: {len(c)}")
    print(f"  Avg Yield: {avg_yield:.1f} bu/ac")
    print(f"  Avg Health Score: {avg_health:.1f}")
    print(f"  Correlation (Health vs Yield): {corr:.3f}")
    print(f"  Top Performers (>=80th percentile): {pct_80}")

print(f"\nOutput Files:")
print(f"  - {output_dir / 'dashboard_by_commodity.png'}")
print(f"  - {output_dir / 'dashboard_by_commodity.pdf'}")