import streamlit as st
import xarray as xr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Satellite Ecosystem Recovery Tracker",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Dark Theme CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1b9e77, #d95f02);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #9aa0a6;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #1e222b;
        border-left: 5px solid #1b9e77;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    .metric-card-danger {
        background: #1e222b;
        border-left: 5px solid #d95f02;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #ffffff;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #adb5bd;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Loading & Caching
# ---------------------------------------------------------
@st.cache_data
def load_data():
    cube_path = "data/processed/august_complex_spectral_cube.nc"
    traj_path = "data/processed/recovery_trajectories.csv"
    
    ds = xr.open_dataset(cube_path)
    df_traj = pd.read_csv(traj_path)
    return ds, df_traj

try:
    ds, df_traj = load_data()
except Exception as e:
    st.error(f"Data loading error: {e}. Please run the notebooks to generate data in data/processed/")
    st.stop()

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.header("🕹️ Dashboard Controls")
st.sidebar.markdown("---")

selected_metric = st.sidebar.selectbox(
    "Select Analysis Layer:",
    ["Delta NBR (Burn Severity)", "NDVI (Vegetation Index)", "NBR (Burn Ratio)"]
)

available_dates = [str(t)[:10] for t in ds["time"].values]
selected_date = st.sidebar.select_slider(
    "Select Observation Milestone:",
    options=available_dates,
    value=available_dates[1], # Default to Post-Fire Oct 2020
    format_func=lambda x: {
        "2020-07-20": "Pre-Fire (Jul 2020)",
        "2020-10-15": "Post-Fire (Oct 2020)",
        "2021-07-20": "Year 1 (Jul 2021)",
        "2022-07-20": "Year 2 (Jul 2022)"
    }.get(x, x)
)

severity_threshold = st.sidebar.slider(
    "High Severity Threshold (dNBR):",
    min_value=0.20, max_value=0.60, value=0.40, step=0.05
)

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Project Highlights")
st.sidebar.info("""
• **Cloud-Native STAC Pipeline**: Sentinel-2 COGs queried via Planetary Computer.
• **Raster Time-Series**: Multi-dimensional xarray & rioxarray calculations.
• **Regeneration Modeling**: Burned perimeter vs. unburned control comparison.
""")

# ---------------------------------------------------------
# Header & Dynamic KPI Metric Cards
# ---------------------------------------------------------
st.markdown('<div class="main-header">Satellite Ecosystem Recovery Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">2020 California Wildfires Case Study (August Complex Fire)</div>', unsafe_allow_html=True)

# Dynamic KPI calculations based on slider threshold
dnbr_arr = ds["dNBR"].values
burned_pixels = np.sum(dnbr_arr > severity_threshold)
total_pixels = dnbr_arr.size
# Each pixel is 30m x 30m (900 m² = 0.09 ha)
burned_area_ha = int(burned_pixels * 0.09)
total_area_ha = int(total_pixels * 0.09)
peak_dnbr = float(np.nanmax(dnbr_arr))
latest_recov = df_traj["Recovery_VRI_Pct"].iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Area Analyzed</div>
        <div class="metric-value">{total_area_ha:,} ha</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card-danger">
        <div class="metric-label">Severe Burn Footprint</div>
        <div class="metric-value">{burned_area_ha:,} ha</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card-danger">
        <div class="metric-label">Peak Burn Severity (dNBR)</div>
        <div class="metric-value">{peak_dnbr:.2f} (High)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">2-Year Recovery (VRI)</div>
        <div class="metric-value">{latest_recov:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Main Tabs Layout
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🗺️ Interactive Spatial Overlays", 
    "📈 Recovery Trajectories & Analytics", 
    "📋 Data & Pipeline Overview"
])

# ---------------------------------------------------------
# TAB 1: Spatial Overlays
# ---------------------------------------------------------
with tab1:
    st.subheader(f"Spatial Overlay: {selected_metric}")
    st.caption(f"Showing observation data for {selected_date} over the August Complex region.")
    
    col_map1, col_map2 = st.columns([1.6, 1])
    
    with col_map1:
        # Generate Plotly Raster Heatmap for selected metric/date
        if "Delta NBR" in selected_metric:
            data_raster = ds["dNBR"].values
            colorscale = "RdYlGn_r"
            title_text = "Delta NBR (Burn Severity)"
            vmin, vmax = -0.1, 0.8
        elif "NDVI" in selected_metric:
            data_raster = ds["NDVI"].sel(time=selected_date).values
            colorscale = "YlGn"
            title_text = f"NDVI Vegetation Index ({selected_date})"
            vmin, vmax = 0.0, 0.8
        else: # NBR
            data_raster = ds["NBR"].sel(time=selected_date).values
            colorscale = "Spectral"
            title_text = f"Normalized Burn Ratio ({selected_date})"
            vmin, vmax = -0.3, 0.6

        fig_spatial = px.imshow(
            data_raster,
            x=ds["lon"].values,
            y=ds["lat"].values,
            color_continuous_scale=colorscale,
            range_color=[vmin, vmax],
            labels={"x": "Longitude", "y": "Latitude", "color": selected_metric},
            title=title_text,
            origin="lower"
        )
        fig_spatial.update_layout(
            template="plotly_dark",
            height=500,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_spatial, use_container_width=True)

    with col_map2:
        st.subheader("Geospatial Map View")
        # Folium interactive Map centered on August Complex
        m = folium.Map(location=[39.95, -123.0], zoom_start=9, tiles="CartoDB dark_matter")
        
        bbox = [-123.55, 39.45, -122.45, 40.55]
        bounds = [[bbox[1], bbox[0]], [bbox[3], bbox[2]]]
        
        folium.Rectangle(
            bounds=bounds,
            color="#1b9e77",
            weight=2,
            fill=True,
            fill_opacity=0.05,
            popup="August Complex Area of Interest"
        ).add_to(m)
        
        # Subsample high severity points for clean performance
        lat_grid = ds["lat"].values
        lon_grid = ds["lon"].values
        step = 18
        for i in range(0, dnbr_arr.shape[0], step):
            for j in range(0, dnbr_arr.shape[1], step):
                val = dnbr_arr[i, j]
                if val > severity_threshold:
                    lat_p = lat_grid[i]
                    lon_p = lon_grid[j]
                    color = "#e41a1c" if val > 0.6 else "#ff7f00" if val > 0.4 else "#ffff33"
                    folium.CircleMarker(
                        location=[lat_p, lon_p],
                        radius=2.5,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7,
                        popup=f"dNBR: {val:.2f}"
                    ).add_to(m)
                    
        st_folium(m, height=450, width=None, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: Recovery Trajectories
# ---------------------------------------------------------
with tab2:
    st.subheader("Spectral Recovery Dynamics (2020–2022)")
    st.caption("Comparing pixel-level spectral trajectories of burned perimeters against unburned control regions.")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        # Determine metric columns based on sidebar selection
        if "NBR" in selected_metric and "Delta" not in selected_metric:
            y_burned = df_traj["Burned_NBR"]
            y_control = df_traj["Control_NBR"]
            ylabel = "NBR Index"
            title = "NBR Trajectory Comparison"
        else:
            y_burned = df_traj["Burned_NDVI"]
            y_control = df_traj["Control_NDVI"]
            ylabel = "NDVI Index"
            title = "NDVI Trajectory Comparison"
            
        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(
            x=df_traj["Date"], y=y_burned,
            mode="lines+markers", name="Burned Perimeter",
            line=dict(color="#d95f02", width=3), marker=dict(size=9)
        ))
        fig_traj.add_trace(go.Scatter(
            x=df_traj["Date"], y=y_control,
            mode="lines+markers", name="Unburned Control",
            line=dict(color="#2ca02c", width=3, dash="dash"), marker=dict(size=9)
        ))
        fig_traj.update_layout(
            title=title,
            xaxis_title="Observation Date",
            yaxis_title=ylabel,
            template="plotly_dark",
            height=420
        )
        st.plotly_chart(fig_traj, use_container_width=True)
        
    with col_t2:
        # Vegetation Regeneration Index Bar Chart
        fig_vri = px.bar(
            df_traj,
            x="Date",
            y="Recovery_VRI_Pct",
            text="Recovery_VRI_Pct",
            title="Vegetation Regeneration Index (VRI %)",
            labels={"Date": "Date", "Recovery_VRI_Pct": "Recovery (%)"},
            color="Recovery_VRI_Pct",
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )
        fig_vri.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_vri.update_layout(height=420, yaxis_range=[0, 115])
        st.plotly_chart(fig_vri, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: Data & Overview
# ---------------------------------------------------------
with tab3:
    st.subheader("Processed Time-Series Dataset")
    st.dataframe(df_traj, use_container_width=True)
    
    st.subheader("Technical Architecture")
    st.markdown("""
    - **Cloud-Native Ingestion**: STAC API queries querying `sentinel-2-l2a` collection via Microsoft Planetary Computer.
    - **Multi-Dimensional Analysis**: Multi-band raster arrays (Red, NIR, SWIR2) processed using `xarray` and `rioxarray`.
    - **Disturbance Mapping**: Delta NBR (`dNBR = NBR_pre - NBR_post`) calculated at 30m resolution to map burn severity.
    - **Recovery Rate Modeling**: Vegetation Regeneration Index (`VRI %`) computed over 24-month window comparing burned vs. control regions.
    """)
