# Final Project - Agricultural Data Analysis

This project analyzes agricultural data including weather conditions, crop yields, and vegetation health using satellite imagery.

## Project Structure

```
.
├── Data/                    # Data files and processing scripts
│   ├── fields.csv          # Field location data
│   ├── fields.geojson      # Field geometries
│   ├── fields_ndvi.geojson # NDVI data for fields
│   ├── weather_data.csv   # Weather data
│   ├── weather_yield_aligned.csv # Aligned weather and yield data
│   ├── vegetation_health.csv # Vegetation health metrics
│   └── *.py               # Data processing scripts
├── output/                 # Generated dashboards and visualizations
│   ├── dashboard_*.png    # Dashboard images
│   ├── dashboard_*.pdf     # Dashboard PDFs
│   └── dashboard_maps.html # Interactive map
├── satellite_bands/        # Satellite band data (empty)
└── README.md              # This file
```

## Data Scripts

- `download_weather.py` - Download weather data
- `generate_fields.py` - Generate field data
- `generate_ndvi.py` - Generate NDVI vegetation indices
- `align_weather_yield.py` - Align weather and yield data
- `create_dashboard.py` - Create main dashboard
- `create_dashboard_by_commodity.py` - Create commodity-specific dashboards
- `create_maps_html.py` - Generate interactive maps

## Dashboard Outputs

Dashboards are generated for each crop:
- Corn
- Wheat
- Soybeans
- Alfalfa

Each dashboard includes:
- Yield trends
- Weather correlation
- Vegetation health indicators
- Regional maps

## Requirements

- Python 3.x
- pandas
- matplotlib
- geopandas
- folium (for interactive maps)
