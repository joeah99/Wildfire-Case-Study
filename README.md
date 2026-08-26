# Satellite Ecosystem Recovery Tracker
### 2020 California Wildfires Case Study (August Complex Fire)

A remote sensing and geospatial analysis project built to track vegetation recovery after the **2020 August Complex Fire** in Northern California—the largest wildfire in CA history, burning over 1 million acres.

This project queries Sentinel-2 satellite imagery via the Microsoft Planetary Computer STAC API to map burn severity and track pixel-level vegetation recovery over a 2-year window (2020–2022).

---

## Project Overview

- **Cloud-Native STAC Pipeline**: Queries Sentinel-2 Cloud-Optimized GeoTIFFs (COGs) over a 2-year window using `pystac_client` and Planetary Computer.
- **Raster Processing**: Processes multi-spectral satellite imagery at 10m–30m resolution using `xarray` and `rioxarray` to compute **NDVI**, **NBR**, and **dNBR** rasters.
- **Vegetation Recovery Modeling**: Segments burned perimeters from unburned control regions to model post-fire regeneration rates over 24 months.
- **Interactive Streamlit App**: A web dashboard (`app.py`) with interactive spatial heatmaps, Folium satellite overlays, Plotly time-series charts, and threshold filters.

---

## How It Works & Spectral Indices

### 1. Normalized Difference Vegetation Index (NDVI)
Measures green vegetation density using Red and Near-Infrared (NIR) bands.
$$\text{NDVI} = \frac{\text{NIR (B08)} - \text{Red (B04)}}{\text{NIR (B08)} + \text{Red (B04)}}$$

### 2. Normalized Burn Ratio (NBR)
Highlights burned areas and vegetation loss by comparing Near-Infrared (NIR) and Short-Wave Infrared (SWIR2).
$$\text{NBR} = \frac{\text{NIR (B08)} - \text{SWIR2 (B12)}}{\text{NIR (B08)} + \text{SWIR2 (B12)}}$$

### 3. Delta NBR (dNBR / Burn Severity)
Calculates the drop in NBR pre- and post-fire. Higher values indicate higher burn severity.
$$\text{dNBR} = \text{NBR}_{\text{pre-fire}} - \text{NBR}_{\text{post-fire}}$$

### 4. Vegetation Recovery Index (VRI %)
Quantifies the percentage of vegetation regrowth relative to the pre-fire baseline.
$$\text{VRI \%} = \frac{\text{NBR}_t - \text{NBR}_{\text{post}}}{\text{NBR}_{\text{pre}} - \text{NBR}_{\text{post}}} \times 100$$

---

## Key Results

- **Area Analyzed**: 121,500 hectares (~300,000 acres) within the August Complex perimeter.
- **Severe Burn Footprint**: ~58,620 hectares ($\text{dNBR} > 0.40$).
- **Year 1 Recovery**: Rebounded to **48.4%** of pre-fire baseline by July 2021.
- **Year 2 Recovery**: Reached **77.6%** recovery by July 2022.

---

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/Wildfire-Case-Study.git
   cd Wildfire-Case-Study
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit Dashboard**:
   ```bash
   streamlit run app.py
   ```

4. **Notebooks**:
   Open and run `01_stac_query_and_nbr.ipynb` and `02_recovery_analysis.ipynb` in VS Code or Jupyter Notebook.

---

## Stack & Libraries

- **Geospatial**: `pystac_client`, `planetary_computer`, `xarray`, `rioxarray`, `geopandas`, `rasterio`
- **Dashboard & Plotting**: `streamlit`, `plotly`, `folium`, `matplotlib`
- **Data Analysis**: `numpy`, `pandas`, `netCDF4`
