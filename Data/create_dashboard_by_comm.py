import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

output_dir = Path(r"C:\Users\aniza\Task 1\Assignment 9\output")
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

weather_annual = weather_yield.groupby('field_id')['annual_precip_mm'].mean().reset_index()
fields = fields.merge(weather_annual, on='field_id', how='left')

commodities = ['Corn', 'Soybeans', 'Wheat', 'Alfalfa']
colors_h = {'Excellent': '#2E7D32', 'Good': '#66BB6A', 'Fair': '#FF9800', 'Poor': '#D32F2F'}
drain_colors = {'Very Poor': '#1565C0', 'Poor': '#42A5F5', 'Somewhat Poor': '#90CAF9', 'Moderately Well': '#81C784', 'Well': '#2E7D32'}
erosion_colors = {'Very Low': '#2E7D32', 'Low': '#66BB6A', 'Moderate': '#FFC107', 'High': '#FF9800', 'Very High': '#D32F2F'}

for comm in commodities:
    comm_fields = fields[fields['commodity_2023'] == comm].copy()
    comm_weather = weather_yield[weather_yield['commodity_2023'] == comm].copy()
    comm_veg = vegetation[vegetation['commodity'] == comm].copy()
    
    fig = plt.figure(figsize=(20, 24))
    fig.suptitle(f'FARM DASHBOARD - {comm.upper()}', fontsize=20, fontweight='bold', y=0.98)
    
    gs = gridspec.GridSpec(5, 3, figure=fig, hspace=0.35, wspace=0.25)
    
    ax1 = fig.add_subplot(gs[0, 0])
    scatter = ax1.scatter(comm_fields['longitude'], comm_fields['latitude'], 
                          c=comm_fields['soil_health_score'], cmap='RdYlGn', 
                          s=comm_fields['field_acres']/2, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title(f'Card 1: Geospatial - Soil Health Score', fontweight='bold')
    plt.colorbar(scatter, ax=ax1, label='Health Score')
    
    ax2 = fig.add_subplot(gs[0, 1])
    scatter2 = ax2.scatter(comm_fields['longitude'], comm_fields['latitude'], 
                           c=comm_fields['avg_yield'], cmap='YlOrRd', 
                           s=comm_fields['field_acres']/2, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.set_title(f'Card 1: Geospatial - Yield (bu/ac)', fontweight='bold')
    plt.colorbar(scatter2, ax=ax2, label='Yield')
    
    ax3 = fig.add_subplot(gs[0, 2])
    scatter3 = ax3.scatter(comm_fields['longitude'], comm_fields['latitude'], 
                           c=comm_fields['avg_ndvi'], cmap='Greens', 
                           s=comm_fields['field_acres']/2, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax3.set_xlabel('Longitude')
    ax3.set_ylabel('Latitude')
    ax3.set_title(f'Card 1: Geospatial - Vegetation (NDVI)', fontweight='bold')
    plt.colorbar(scatter3, ax=ax3, label='NDVI')
    
    ax4 = fig.add_subplot(gs[1, 0])
    for year in [2023, 2024, 2025]:
        year_data = comm_weather[comm_weather['year'] == year]
        ax4.plot(year_data['year'], year_data['avg_temp_c'], marker='o', label=str(year), linewidth=2)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Temperature (°C)')
    ax4.set_title(f'Card 2: Weather Time Series - Temperature', fontweight='bold')
    ax4.legend()
    
    ax5 = fig.add_subplot(gs[1, 1])
    precip_by_year = comm_weather.groupby('year')['annual_precip_mm'].mean()
    ax5.bar(precip_by_year.index.astype(str), precip_by_year.values, color='#2196F3', alpha=0.8)
    ax5.set_xlabel('Year')
    ax5.set_ylabel('Precipitation (mm)')
    ax5.set_title(f'Card 2: Weather Time Series - Precipitation', fontweight='bold')
    
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.scatter(comm_weather['avg_temp_c'], comm_weather['yield_bu_ac'], 
                c=comm_weather['annual_precip_mm'], cmap='Blues', s=60, alpha=0.7, edgecolors='black')
    ax6.set_xlabel('Avg Temperature (°C)')
    ax6.set_ylabel('Yield (bu/ac)')
    ax6.set_title(f'Card 2: Weather vs Yield', fontweight='bold')
    
    ax7 = fig.add_subplot(gs[2, 0])
    health_counts = comm_fields['health_rating'].value_counts()
    colors = [colors_h.get(r, 'gray') for r in health_counts.index]
    if len(health_counts) > 0:
        ax7.pie(health_counts, labels=[f"{l}\n({c})" for l, c in zip(health_counts.index, health_counts.values)], 
                autopct='', colors=colors, startangle=90)
    ax7.set_title(f'Card 3: Soil Health - Rating Distribution', fontweight='bold')
    
    ax8 = fig.add_subplot(gs[2, 1])
    soil_metrics = ['organic_matter_pct', 'pH', 'CEC_meq_100g', 'topsoil_depth_cm']
    soil_means = [comm_fields[m].mean() for m in soil_metrics]
    soil_stds = [comm_fields[m].std() for m in soil_metrics]
    x_pos = np.arange(len(soil_metrics))
    ax8.bar(x_pos, soil_means, yerr=soil_stds, capsize=5, color=['#4CAF50', '#2196F3', '#9C27B0', '#FF9800'], alpha=0.8)
    ax8.set_xticks(x_pos)
    ax8.set_xticklabels(['OM (%)', 'pH', 'CEC', 'Topsoil\n(cm)'])
    ax8.set_ylabel('Value')
    ax8.set_title(f'Card 3: Soil Health - Key Indicators', fontweight='bold')
    
    ax9 = fig.add_subplot(gs[2, 2])
    erosion_counts = comm_fields['erosion_risk'].value_counts()
    ax9.barh(erosion_counts.index, erosion_counts.values, 
             color=[erosion_colors.get(e, 'gray') for e in erosion_counts.index])
    ax9.set_xlabel('Number of Fields')
    ax9.set_title(f'Card 3: Soil Health - Erosion Risk', fontweight='bold')
    
    ax10 = fig.add_subplot(gs[3, 0])
    ndvi_by_month = comm_veg.groupby('month')['ndvi'].mean()
    colors_seasonal = ['#BBDEFB' if m in [1,2,12] else '#C8E6C9' if m in [3,4,5] else '#81C784' if m in [6,7,8] else '#FFECB3' for m in ndvi_by_month.index]
    ax10.bar(ndvi_by_month.index, ndvi_by_month.values, color=colors_seasonal)
    ax10.set_xlabel('Month')
    ax10.set_ylabel('Mean NDVI')
    ax10.set_title(f'Card 4: Vegetation Health - Seasonal', fontweight='bold')
    ax10.set_xticks(range(1, 13))
    
    ax11 = fig.add_subplot(gs[3, 1])
    ndvi_yearly = comm_veg.groupby('year')['ndvi'].mean()
    ax11.plot(ndvi_yearly.index, ndvi_yearly.values, marker='o', linewidth=3, markersize=10, color='#2E7D32')
    ax11.fill_between(ndvi_yearly.index, ndvi_yearly.values, alpha=0.3, color='#2E7D32')
    ax11.set_xlabel('Year')
    ax11.set_ylabel('Mean NDVI')
    ax11.set_title(f'Card 4: Vegetation Health - Annual Trend', fontweight='bold')
    ax11.set_xticks([2023, 2024, 2025])
    
    ax12 = fig.add_subplot(gs[3, 2])
    scatter_ndvi = ax12.scatter(comm_fields['soil_health_score'], comm_fields['avg_yield'], 
                                c=comm_fields['avg_ndvi'], cmap='Greens', s=60, alpha=0.7, edgecolors='black')
    ax12.set_xlabel('Soil Health Score')
    ax12.set_ylabel('Yield (bu/ac)')
    ax12.set_title(f'Card 4: Health vs Yield vs NDVI', fontweight='bold')
    plt.colorbar(scatter_ndvi, ax=ax12, label='NDVI')
    
    corr_cols = ['soil_health_score', 'avg_yield', 'avg_ndvi', 'annual_precip_mm']
    corr_data = comm_fields[corr_cols].dropna()
    corr_matrix = corr_data.corr() if len(corr_data) > 0 else None
    
    ax13 = fig.add_subplot(gs[4, 0])
    if corr_matrix is not None:
        sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn', center=0, ax=ax13, fmt='.2f', 
                    square=True, linewidths=0.5, cbar_kws={'shrink': 0.8})
    ax13.set_title(f'Card 5: EDA - Correlation Matrix', fontweight='bold')
    
    ax14 = fig.add_subplot(gs[4, 1])
    ax14.scatter(comm_fields['soil_health_score'], comm_fields['avg_yield'], 
                 c=comm_fields['avg_ndvi'], cmap='Greens', s=60, alpha=0.7, edgecolors='black')
    ax14.set_xlabel('Soil Health Score')
    ax14.set_ylabel('Yield (bu/ac)')
    ax14.set_title(f'Card 5: EDA - Health vs Yield', fontweight='bold')
    
    ax15 = fig.add_subplot(gs[4, 2])
    ax15.scatter(comm_fields['organic_matter_pct'], comm_fields['avg_yield'], 
                 s=60, alpha=0.7, edgecolors='black', color='#4CAF50')
    ax15.set_xlabel('Organic Matter (%)')
    ax15.set_ylabel('Yield (bu/ac)')
    ax15.set_title(f'Card 5: EDA - OM vs Yield', fontweight='bold')
    
    filename = f'dashboard_{comm.lower()}.png'
    fig.savefig(output_dir / filename, dpi=150, bbox_inches='tight', facecolor='white')
    fig.savefig(output_dir / filename.replace('.png', '.pdf'), bbox_inches='tight', facecolor='white')
    plt.close(fig)
    
    corr_value = comm_fields['soil_health_score'].corr(comm_fields['avg_yield'])
    print(f"{comm}: Fields={len(comm_fields)}, Avg Yield={comm_fields['avg_yield'].mean():.1f}, "
          f"Avg Health={comm_fields['soil_health_score'].mean():.1f}, Corr={corr_value:.3f}")

print(f"\nSaved to {output_dir}/")
print("Files: dashboard_corn.png/pdf, dashboard_soybeans.png/pdf, dashboard_wheat.png/pdf, dashboard_alfalfa.png/pdf")