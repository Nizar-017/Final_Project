import pandas as pd
import numpy as np

np.random.seed(123)

field_names_2 = [
    "Prairie Wind", "Golden Harvest", "Sunny Slope", "Rolling Hills", "Meadow Brook",
    "Old Farmstead", "River Valley", "Creek Side", "Hilltop View", "Valley Floor",
    "North Pasture", "South Meadow", "East Ridge", "West Field", "Center Pasture",
    "Corner Plot", "Back Forty", "Front Acres", "Home Farm", "Cross Creek",
    "Deep Water", "Sandy Loam", "Clay Bank", "Gravel Pit", "Timber Edge",
    "Oak Hill", "Maple Grove", "Cedar Lane", "Pine Ridge", "Birch Run",
    "Willow Bend", "Elm Creek", "Ash Grove", "Spruce Point", "Fir Branch",
    "Juniper Field", "Cypress Swamp", "Redbud Patch", "Dogwood Corner", "Magnolia Plot",
    "Hickory Hollow", "Walnut Grove", "Chestnut Hill", "Sycamore Ridge", "Poplar Field",
    "Cotton Row", "Tobacco Barn", "Corn Patch", "Soybean Field", "Wheat Acre",
    "Alfalfa Stand", "Clover Field", "Bluegrass Pasture", "Fescue Meadow", "Timothy Lot",
    "Brome Grass", "Orchard Row", "Vineyard Hill", "Berry Patch", "Vegetable Plot",
    "Garden Row", "Orchard Acre", "Fruit Grove", "Nut Orchard", "Silage Field",
    "Cover Crop", "Green Manure", "Fallow Ground", "Set Aside", "Conservation Area",
    "Wetland Buffer", "Filter Strip", "Grass Waterway", "Terrace Row", "Contour Strip",
    "Windbreak Lane", "Shelter Belt", "Hedgerow Field", "Pollinator Patch", "Wildlife Food Plot",
    "Native Prairie", "Restored Wetland", "Woodland Edge", "Riparian Zone", "Steep Pasture",
    "Gentle Slope", "Level Terrain", "Rolling Upland", "Bottom Floodplain", "Terrace Top",
    "Hill Shoulder", "Valley Bottom", "Plateau Field", "Escarpment Edge", "Draw Meadow",
    "Seepage Area", "Spring Fed", "Rainwater Catch", "Irrigation Plot", "Dry Land Acre"
]

commodities = ["Corn", "Soybeans", "Wheat", "Alfalfa"]
drainage_classes = ["Very Poor", "Poor", "Somewhat Poor", "Moderately Well", "Well"]

base_lat = 41.9
base_lon = -93.6

data = []

for i in range(100):
    field_id = f"F{i+101:03d}"
    field_name = field_names_2[i]
    
    commodity = np.random.choice(commodities)
    drainage = np.random.choice(drainage_classes, p=[0.05, 0.20, 0.20, 0.25, 0.30])
    
    if drainage == "Well":
        om = np.random.uniform(3.5, 5.5)
        cec = np.random.uniform(18, 26)
        bd = np.random.uniform(1.05, 1.25)
        awc = np.random.uniform(0.18, 0.24)
        topsoil = np.random.randint(28, 42)
        k_factor = np.random.uniform(0.15, 0.22)
    elif drainage == "Moderately Well":
        om = np.random.uniform(2.5, 4.0)
        cec = np.random.uniform(14, 20)
        bd = np.random.uniform(1.20, 1.40)
        awc = np.random.uniform(0.14, 0.20)
        topsoil = np.random.randint(20, 32)
        k_factor = np.random.uniform(0.22, 0.30)
    elif drainage == "Somewhat Poor":
        om = np.random.uniform(2.0, 3.5)
        cec = np.random.uniform(10, 16)
        bd = np.random.uniform(1.30, 1.50)
        awc = np.random.uniform(0.12, 0.18)
        topsoil = np.random.randint(16, 26)
        k_factor = np.random.uniform(0.28, 0.38)
    elif drainage == "Poor":
        om = np.random.uniform(1.2, 2.5)
        cec = np.random.uniform(7, 13)
        bd = np.random.uniform(1.40, 1.58)
        awc = np.random.uniform(0.08, 0.14)
        topsoil = np.random.randint(10, 20)
        k_factor = np.random.uniform(0.35, 0.48)
    else:
        om = np.random.uniform(3.0, 5.5)
        cec = np.random.uniform(15, 26)
        bd = np.random.uniform(1.02, 1.20)
        awc = np.random.uniform(0.20, 0.26)
        topsoil = np.random.randint(35, 48)
        k_factor = np.random.uniform(0.10, 0.18)
    
    ph = np.random.uniform(5.5, 7.5)
    sand = np.random.randint(20, 70)
    silt = np.random.randint(15, 50)
    clay = 100 - sand - silt
    ec = np.random.uniform(0.3, 2.0) if drainage != "Well" else np.random.uniform(0.3, 0.8)
    
    if k_factor < 0.25:
        slope = np.random.uniform(0.5, 3.0)
    elif k_factor < 0.35:
        slope = np.random.uniform(2.5, 6.0)
    else:
        slope = np.random.uniform(5.0, 11.0)
    
    lat = base_lat + np.random.uniform(-0.15, 0.15)
    lon = base_lon + np.random.uniform(-0.15, 0.15)
    
    acres = np.random.randint(50, 250)
    
    if commodity == "Corn":
        base_yield = 180 + (om * 10) + (topsoil * 0.5) - (slope * 2)
        y2023 = max(120, base_yield + np.random.uniform(-15, 15))
        y2024 = max(120, base_yield + np.random.uniform(-15, 15))
        y2025 = max(120, base_yield + np.random.uniform(-15, 15))
    elif commodity == "Soybeans":
        base_yield = 45 + (om * 5) + (topsoil * 0.3) - (slope * 1)
        y2023 = max(30, base_yield + np.random.uniform(-5, 5))
        y2024 = max(30, base_yield + np.random.uniform(-5, 5))
        y2025 = max(30, base_yield + np.random.uniform(-5, 5))
    elif commodity == "Wheat":
        base_yield = 45 + (om * 4) + (topsoil * 0.2) - (slope * 1.5)
        y2023 = max(25, base_yield + np.random.uniform(-5, 5))
        y2024 = max(25, base_yield + np.random.uniform(-5, 5))
        y2025 = max(25, base_yield + np.random.uniform(-5, 5))
    else:
        base_yield = 7 + (om * 0.5) + (topsoil * 0.05)
        y2023 = max(4, base_yield + np.random.uniform(-1, 1))
        y2024 = max(4, base_yield + np.random.uniform(-1, 1))
        y2025 = max(4, base_yield + np.random.uniform(-1, 1))
    
    data.append({
        'field_id': field_id,
        'field_name': field_name,
        'organic_matter_pct': round(om, 1),
        'pH': round(ph, 1),
        'CEC_meq_100g': round(cec, 1),
        'bulk_density_g_cm3': round(bd, 2),
        'available_water_capacity_cm': round(awc, 2),
        'sand_pct': sand,
        'silt_pct': silt,
        'clay_pct': clay,
        'EC_dS_m': round(ec, 1),
        'field_acres': acres,
        'location': 'IA',
        'latitude': round(lat, 2),
        'longitude': round(lon, 2),
        'k_factor': round(k_factor, 2),
        'slope_pct': round(slope, 1),
        'topsoil_depth_cm': topsoil,
        'commodity_2023': commodity,
        'yield_2023_bu_ac': round(y2023, 1),
        'commodity_2024': commodity,
        'yield_2024_bu_ac': round(y2024, 1),
        'commodity_2025': commodity,
        'yield_2025_bu_ac': round(y2025, 1),
        'drainage_class': drainage
    })

df = pd.DataFrame(data)
df.to_csv('fields_batch2.csv', index=False)

print(f"Generated {len(df)} fields (F101-F200)")
print(f"\nCommodity distribution:")
print(df['commodity_2023'].value_counts())
print(f"\nDrainage class distribution:")
print(df['drainage_class'].value_counts())
print(f"\nData summary:")
print(f"  Avg OM: {df['organic_matter_pct'].mean():.1f}%")
print(f"  Avg pH: {df['pH'].mean():.1f}")
print(f"  Avg CEC: {df['CEC_meq_100g'].mean():.1f}")
print(f"  Avg Yield: {((df['yield_2023_bu_ac'] + df['yield_2024_bu_ac'] + df['yield_2025_bu_ac'])/3).mean():.1f} bu/ac")
print(f"  Total Acres: {df['field_acres'].sum()}")