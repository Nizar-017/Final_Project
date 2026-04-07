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
def generate_alerts(comm_fields, comm_veg):
    alerts = {'critical': [], 'high': [], 'medium': [], 'findings': [], 'recommendations': []}
    
    low_ndvi = (comm_fields['avg_ndvi'] < 0.3).sum()
    med_ndvi = ((comm_fields['avg_ndvi'] >= 0.3) & (comm_fields['avg_ndvi'] < 0.5)).sum()
    if low_ndvi > 0:
        alerts['critical'].append(f'Low vegetation index detected ({low_ndvi} fields) - recommended immediate scouting for nitrogen deficiency or pest pressure')
    if med_ndvi > 0:
        alerts['high'].append(f'Medium vegetation health ({med_ndvi} fields) - consider foliar feeding or pest inspection')
    
    poor_health = (comm_fields['soil_health_score'] < 40).sum()
    fair_health = ((comm_fields['soil_health_score'] >= 40) & (comm_fields['soil_health_score'] < 60)).sum()
    if poor_health > 0:
        alerts['critical'].append(f'Poor soil health ({poor_health} fields) - immediate soil amendment required')
    if fair_health > 0:
        alerts['high'].append(f'Fair soil health ({fair_health} fields) - enhance organic matter, improve drainage')
    
    low_om = (comm_fields['organic_matter_pct'] < 2).sum()
    if low_om > 0:
        alerts['high'].append(f'Low organic matter detected ({low_om} fields) - apply cover crops, manure, or compost')
    
    poor_drain = (comm_fields['drainage_class'].isin(['Poor', 'Very Poor'])).sum()
    if poor_drain > 0:
        alerts['high'].append(f'Poor drainage conditions ({poor_drain} fields) - consider drainage tiles or land grading')
    
    high_bd = (comm_fields['bulk_density_g_cm3'] > 1.5).sum()
    if high_bd > 0:
        alerts['medium'].append(f'Soil compaction risk detected ({high_bd} fields) - consider deep tillage or cover crops')
    
    high_erosion = comm_fields['erosion_risk'].isin(['High', 'Very High']).sum()
    if high_erosion > 0:
        alerts['medium'].append(f'Erosion risk identified ({high_erosion} fields) - install terraces or cover crops')
    
    corr = comm_fields['soil_health_score'].corr(comm_fields['avg_yield'])
    top_performers = (comm_fields['yield_percentile'] >= 80).sum()
    alerts['findings'].append(f'Health-Yield Correlation: {corr:.2f} (Strong positive relationship)')
    alerts['findings'].append(f'Top performing fields (>=80th percentile): {top_performers} fields')
    alerts['findings'].append(f'Fields requiring attention: {fair_health + poor_health} fields')
    
    if low_ndvi > 0:
        alerts['recommendations'].append('1. Inspect low-NDVI fields for pest infestation or nutrient deficiency')
    if low_om > 0:
        alerts['recommendations'].append('2. Apply organic amendments (compost, manure, cover crops) to low-OM fields')
    if poor_drain > 0:
        alerts['recommendations'].append('3. Implement drainage improvements for poorly drained fields')
    if high_erosion > 0:
        alerts['recommendations'].append('4. Establish erosion control measures (terraces, cover crops, buffer strips)')
    
    return alerts
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
erosion_colors = {'Very Low': '#2E7D32', 'Low': '#66BB6A', 'Moderate': '#FFC107', 'High': '#FF9800', 'Very High': '#D32F2F'}
for comm in commodities:
    comm_fields = fields[fields['commodity_2023'] == comm].copy()
    comm_weather = weather_yield[weather_yield['commodity_2023'] == comm].copy()
    comm_veg = vegetation[vegetation['commodity'] == comm].copy()
    alerts = generate_alerts(comm_fields, comm_veg)
    
    fig = plt.figure(figsize=(20, 28))
    fig.suptitle(f'FARM DASHBOARD - {comm.upper()}', fontsize=22, fontweight='bold', y=0.99)
    
    gs = gridspec.GridSpec(6, 3, figure=fig, hspace=0.35, wspace=0.25, height_ratios=[1,1,1,1,1,1.5])
    
    # Cards 1-5 (Visual Only)
    ax1 = fig.add_subplot(gs[0, 0])
    scatter = ax1.scatter(comm_fields['longitude'], comm_fields['latitude'], c=comm_fields['soil_health_score'], cmap='RdYlGn', s=comm_fields['field_acres']/2, alpha=0.7, edgecolors='black')
    ax1.set_xlabel('Longitude'); ax1.set_ylabel('Latitude')
    ax1.set_title('Card 1: Soil Health Score', fontweight='bold', fontsize=11)
    plt.colorbar(scatter, ax=ax1, label='Score')
    
    ax2 = fig.add_subplot(gs[0, 1])
    scatter2 = ax2.scatter(comm_fields['longitude'], comm_fields['latitude'], c=comm_fields['avg_yield'], cmap='YlOrRd', s=comm_fields['field_acres']/2, alpha=0.7, edgecolors='black')
    ax2.set_xlabel('Longitude'); ax2.set_ylabel('Latitude')
    ax2.set_title('Card 1: Yield (bu/ac)', fontweight='bold', fontsize=11)
    plt.colorbar(scatter2, ax=ax2, label='Yield')
    
    ax3 = fig.add_subplot(gs[0, 2])
    scatter3 = ax3.scatter(comm_fields['longitude'], comm_fields['latitude'], c=comm_fields['avg_ndvi'], cmap='Greens', s=comm_fields['field_acres']/2, alpha=0.7, edgecolors='black')
    ax3.set_xlabel('Longitude'); ax3.set_ylabel('Latitude')
    ax3.set_title('Card 1: NDVI', fontweight='bold', fontsize=11)
    plt.colorbar(scatter3, ax=ax3, label='NDVI')
    
    ax4 = fig.add_subplot(gs[1, 0])
    precip = comm_weather.groupby('year')['annual_precip_mm'].mean()
    ax4.bar(precip.index.astype(str), precip.values, color='#2196F3', alpha=0.8)
    ax4.set_xlabel('Year'); ax4.set_ylabel('mm')
    ax4.set_title('Card 2: Precipitation', fontweight='bold', fontsize=11)
    
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.scatter(comm_weather['avg_temp_c'], comm_weather['yield_bu_ac'], c=comm_weather['annual_precip_mm'], cmap='Blues', s=60, alpha=0.7, edgecolors='black')
    ax5.set_xlabel('Temp (°C)'); ax5.set_ylabel('Yield')
    ax5.set_title('Card 2: Weather vs Yield', fontweight='bold', fontsize=11)
    
    ax6 = fig.add_subplot(gs[1, 2])
    temp = comm_weather.groupby('year')['avg_temp_c'].mean()
    ax6.plot(temp.index, temp.values, marker='o', linewidth=2, color='#FF5722', markersize=8)
    ax6.set_xlabel('Year'); ax6.set_ylabel('°C')
    ax6.set_title('Card 2: Temperature', fontweight='bold', fontsize=11)
    
    ax7 = fig.add_subplot(gs[2, 0])
    hc = comm_fields['health_rating'].value_counts()
    ax7.pie(hc, labels=[f"{l}\n({c})" for l, c in zip(hc.index, hc.values)], autopct='', colors=[colors_h.get(r,'gray') for r in hc.index], startangle=90)
    ax7.set_title('Card 3: Health Rating', fontweight='bold', fontsize=11)
    
    ax8 = fig.add_subplot(gs[2, 1])
    metrics = ['OM', 'pH', 'CEC', 'Topsoil']
    means = [comm_fields['organic_matter_pct'].mean(), comm_fields['pH'].mean()/7, comm_fields['CEC_meq_100g'].mean()/20, comm_fields['topsoil_depth_cm'].mean()/40]
    ax8.bar(metrics, means, color=['#4CAF50','#2196F3','#9C27B0','#FF9800'], alpha=0.8)
    ax8.set_title('Card 3: Soil Indicators', fontweight='bold', fontsize=11)
    ax8.set_ylim(0, 1.2)
    
    ax9 = fig.add_subplot(gs[2, 2])
    ec = comm_fields['erosion_risk'].value_counts()
    ax9.barh(ec.index, ec.values, color=[erosion_colors.get(e,'gray') for e in ec.index])
    ax9.set_xlabel('Fields')
    ax9.set_title('Card 3: Erosion Risk', fontweight='bold', fontsize=11)
    
    ax10 = fig.add_subplot(gs[3, 0])
    ndvi_month = comm_veg.groupby('month')['ndvi'].mean()
    ax10.bar(ndvi_month.index, ndvi_month.values, color='#81C784', alpha=0.8)
    ax10.set_xlabel('Month'); ax10.set_ylabel('NDVI')
    ax10.set_title('Card 4: Seasonal NDVI', fontweight='bold', fontsize=11)
    ax10.set_xticks(range(1,13))
    
    ax11 = fig.add_subplot(gs[3, 1])
    ndvi_year = comm_veg.groupby('year')['ndvi'].mean()
    ax11.plot(ndvi_year.index, ndvi_year.values, marker='o', linewidth=2, color='#2E7D32', markersize=8)
    ax11.set_xlabel('Year'); ax11.set_ylabel('NDVI')
    ax11.set_title('Card 4: Annual Trend', fontweight='bold', fontsize=11)
    
    ax12 = fig.add_subplot(gs[3, 2])
    ax12.scatter(comm_fields['soil_health_score'], comm_fields['avg_yield'], c=comm_fields['avg_ndvi'], cmap='Greens', s=60, alpha=0.7, edgecolors='black')
    ax12.set_xlabel('Health'); ax12.set_ylabel('Yield')
    ax12.set_title('Card 4: Health vs Yield', fontweight='bold', fontsize=11)
    
    corr_cols = ['soil_health_score', 'avg_yield', 'avg_ndvi', 'annual_precip_mm']
    corr_data = comm_fields[corr_cols].dropna()
    
    ax13 = fig.add_subplot(gs[4, 0])
    if len(corr_data) > 0:
        sns.heatmap(corr_data.corr(), annot=True, cmap='RdYlGn', center=0, ax=ax13, fmt='.2f', square=True, linewidths=0.5, cbar_kws={'shrink': 0.8})
    ax13.set_title('Card 5: Correlation Matrix', fontweight='bold', fontsize=11)
    
    ax14 = fig.add_subplot(gs[4, 1])
    ax14.scatter(comm_fields['organic_matter_pct'], comm_fields['avg_yield'], s=60, alpha=0.7, edgecolors='black', color='#4CAF50')
    ax14.set_xlabel('OM (%)'); ax14.set_ylabel('Yield')
    ax14.set_title('Card 5: OM vs Yield', fontweight='bold', fontsize=11)
    
    ax15 = fig.add_subplot(gs[4, 2])
    ax15.scatter(comm_fields['soil_health_score'], comm_fields['avg_yield'], c=comm_fields['avg_ndvi'], cmap='Greens', s=60, alpha=0.7, edgecolors='black')
    ax15.set_xlabel('Health Score'); ax15.set_ylabel('Yield')
    ax15.set_title('Card 5: Health vs Yield', fontweight='bold', fontsize=11)
    
    # Row 6: Consolidated Analysis Section (IMPROVED SPACING)
    ax_analysis = fig.add_subplot(gs[5, :])
    ax_analysis.axis('off')
    
    # SUMMARY BAR
    y = 0.95
    ax_analysis.text(0.5, y, f"SUMMARY: Fields={len(comm_fields)} | Avg Yield={comm_fields['avg_yield'].mean():.1f} bu/ac | Health Score={comm_fields['soil_health_score'].mean():.1f} | Correlation={comm_fields['soil_health_score'].corr(comm_fields['avg_yield']):.2f} | NDVI={comm_fields['avg_ndvi'].mean():.3f} | Total Acres={comm_fields['field_acres'].sum():.0f}", 
                    transform=ax_analysis.transAxes, fontsize=10, ha='center', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2))
    
    # CRITICAL ALERTS
    y = 0.82
    if alerts['critical']:
        ax_analysis.text(0.02, y, "🔴 CRITICAL ALERTS", transform=ax_analysis.transAxes, fontsize=12, fontweight='bold', color='#D32F2F',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFCDD2', edgecolor='#D32F2F', linewidth=1))
        y -= 0.07
        for a in alerts['critical']:
            ax_analysis.text(0.05, y, f"• {a}", transform=ax_analysis.transAxes, fontsize=9, color='#B71C1C', wrap=True, family='monospace')
            y -= 0.06
    
    # HIGH PRIORITY
    y -= 0.03
    if alerts['high']:
        ax_analysis.text(0.02, y, "🟠 HIGH PRIORITY", transform=ax_analysis.transAxes, fontsize=12, fontweight='bold', color='#E65100',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE0B2', edgecolor='#E65100', linewidth=1))
        y -= 0.07
        for a in alerts['high']:
            ax_analysis.text(0.05, y, f"• {a}", transform=ax_analysis.transAxes, fontsize=9, color='#BF360C', wrap=True, family='monospace')
            y -= 0.06
    
    # MEDIUM PRIORITY
    y -= 0.03
    if alerts['medium']:
        ax_analysis.text(0.02, y, "🟡 MEDIUM PRIORITY", transform=ax_analysis.transAxes, fontsize=12, fontweight='bold', color='#F57C00',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9C4', edgecolor='#F57C00', linewidth=1))
        y -= 0.07
        for a in alerts['medium']:
            ax_analysis.text(0.05, y, f"• {a}", transform=ax_analysis.transAxes, fontsize=9, color='#E65100', wrap=True, family='monospace')
            y -= 0.06
    
    # KEY FINDINGS
    y -= 0.03
    if alerts['findings']:
        ax_analysis.text(0.02, y, "📊 KEY FINDINGS", transform=ax_analysis.transAxes, fontsize=12, fontweight='bold', color='#1565C0',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#BBDEFB', edgecolor='#1565C0', linewidth=1))
        y -= 0.07
        for f in alerts['findings']:
            ax_analysis.text(0.05, y, f"• {f}", transform=ax_analysis.transAxes, fontsize=9, color='#0D47A1', wrap=True, family='monospace')
            y -= 0.06
    
    # RECOMMENDATIONS
    y -= 0.03
    if alerts['recommendations']:
        ax_analysis.text(0.02, y, "💡 RECOMMENDATIONS", transform=ax_analysis.transAxes, fontsize=12, fontweight='bold', color='#2E7D32',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=1))
        y -= 0.07
        for r in alerts['recommendations']:
            ax_analysis.text(0.05, y, f"{r}", transform=ax_analysis.transAxes, fontsize=9, color='#1B5E20', wrap=True, family='monospace')
            y -= 0.06
    
    fig.savefig(output_dir / f'dashboard_{comm.lower()}.png', dpi=150, bbox_inches='tight', facecolor='white')
    fig.savefig(output_dir / f'dashboard_{comm.lower()}.pdf', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"{comm}: Dashboard saved to output/")
print(f"\n✅ All dashboards saved to {output_dir}/")
print("Files: dashboard_corn.png/pdf, dashboard_soybeans.png/pdf, dashboard_wheat.png/pdf, dashboard_alfalfa.png/pdf")