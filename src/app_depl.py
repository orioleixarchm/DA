#Loading Packages
# Loading Packages
import json
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import folium
from folium.plugins import FastMarkerCluster
import os
from io import BytesIO
import requests
from utilities import add_marker, add_circle_marker, centered_metric, load_data

# ---------------------------------------------------------------------------
# Data loading — cached once, never re-downloaded on filter change
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Loading data...")
def load_data(url, postalcode=0):
    response = requests.get(url)
    file_stream = BytesIO(response.content)
    if postalcode == 0:
        return pd.read_excel(file_stream, engine='openpyxl')
    else:
        return pd.read_excel(file_stream, engine='openpyxl', dtype={'Postal Code': 'str'})

links = [
    "https://drive.google.com/uc?id=1x4Ph_EfAo1994I4JVrGwPDmi0y-Vtt0q&export=download",
    "https://drive.google.com/uc?id=19i47foVILPjmA4RyKP4WEBQFXSEvLyEe&export=download",
    "https://drive.google.com/uc?id=12UFMCiZhiIhau1dNUBUdPaOm_KBGVOhw&export=download",
]

hotspots   = load_data(links[0], postalcode=1)
greenspots = load_data(links[1], postalcode=0)
bluespots  = load_data(links[2], postalcode=0)

# ---------------------------------------------------------------------------
# Base map HTML — AED + ambulance markers only, cached once forever
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Building map...")
def get_base_map_html():
    brussels_coordinates = [50.8503, 4.3517]
    m = folium.Map(location=brussels_coordinates, zoom_start=12)
    for _, row in greenspots.iterrows():
        add_marker(row, m, 'green', 'plus-sign', f"AED: {row['id']}")
    for _, row in bluespots.iterrows():
        add_marker(row, m, 'blue', 'plus-sign', f"Ambulance: {row['id']}")
    return m.get_root().render()

# ---------------------------------------------------------------------------
# Hotspot layer HTML — built fast using a single GeoJson layer (not per-row
# CircleMarker loop). Cached per unique filtered subset.
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def get_hotspot_layer_html(subset_json: str) -> str:
    """
    Builds ONLY the hotspot markers as a standalone Folium map fragment,
    then extracts just the JavaScript that defines the GeoJSON layer.
    We embed this JS into the base map HTML so both layers share one map.
    """
    subset = pd.read_json(subset_json, dtype={'Postal Code': 'str'})

    if subset.empty:
        return ""

    subset = subset.copy()
    subset['_code_factor'] = pd.factorize(subset['Event Code'])[0]
    n = subset['_code_factor'].nunique()
    cmap = plt.get_cmap('Set1', n)
    code_to_color = {i: colors.rgb2hex(cmap(i % cmap.N)) for i in range(n)}
    subset['_color'] = subset['_code_factor'].map(code_to_color)

    # Build GeoJSON FeatureCollection
    features = []
    for _, row in subset.iterrows():
        aed_dist = round(float(row['AED_distance']), 1) if pd.notna(row.get('AED_distance')) else "N/A"
        amb_dist = round(float(row['Ambulance_distance']), 1) if pd.notna(row.get('Ambulance_distance')) else "N/A"
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(row['Longitude']), float(row['Latitude'])]},
            "properties": {
                "color":    row['_color'],
                "event":    str(row['Event Code']),
                "aed":      aed_dist,
                "amb":      amb_dist,
                "dead":     str(row['Dead']),
            }
        })
    geojson = {"type": "FeatureCollection", "features": features}

    # Use a temporary Folium map just to render the GeoJson layer HTML
    tmp = folium.Map(location=[50.8503, 4.3517], zoom_start=12)
    folium.GeoJson(
        geojson,
        style_function=lambda f: {
            "radius":      5,
            "fillColor":   f["properties"]["color"],
            "color":       f["properties"]["color"],
            "weight":      1,
            "fillOpacity": 0.85,
        },
        marker=folium.CircleMarker(radius=5),
        popup=folium.GeoJsonPopup(
            fields=["event", "aed", "amb", "dead"],
            aliases=["Event:", "AED (m):", "Ambulance (m):", "Fatal:"],
        ),
    ).add_to(tmp)

    # Render and extract only the layer script block (not the full map HTML)
    full_html = tmp.get_root().render()

    # Pull out everything between the two marker script tags
    import re
    # Extract all <script> blocks that reference our geojson layer variable
    scripts = re.findall(r'(<script>[^<]*geo_json[^<]*</script>)', full_html, re.DOTALL)
    return "\n".join(scripts)


# ---------------------------------------------------------------------------
# Merge base map + hotspot layer into final HTML
# ---------------------------------------------------------------------------

def build_final_map_html(hotspot_scripts: str) -> str:
    base_html = get_base_map_html()
    if hotspot_scripts:
        base_html = base_html.replace("</body>", hotspot_scripts + "\n</body>")
    return base_html


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.markdown(
    "<h1 style='text-align: center;'>AED Coverage and Cardiac Arrest Hotspots in Brussels</h1>",
    unsafe_allow_html=True
)

# --- Filters ----------------------------------------------------------------

intervention_type = st.selectbox('Intervention Criticallity:', ('All', 'Fatal', 'Non-Fatal', 'Critical location'))

if intervention_type == 'Critical location':
    aed_distance       = st.number_input('Set critical distance to AED (meters)',       min_value=0, value=500)
    ambulance_distance = st.number_input('Set critical distance to Ambulance (meters)', min_value=0, value=3000)
    interv_subset = hotspots.loc[
        (hotspots['AED_distance'] > aed_distance) &
        (hotspots['Ambulance_distance'] > ambulance_distance)
    ]
elif intervention_type == 'Fatal':
    interv_subset = hotspots[hotspots['Dead'] == 'Yes']
elif intervention_type == 'Non-Fatal':
    interv_subset = hotspots[hotspots['Dead'] == 'No']
else:
    interv_subset = hotspots

event_codes_options = ['All'] + sorted(interv_subset['Event Code'].unique().astype(str))
event_code = st.selectbox('Event code:', event_codes_options)
if event_code != 'All':
    interv_subset = interv_subset[interv_subset['Event Code'] == event_code]

postal_codes_options = ['All'] + sorted(interv_subset['Postal Code'].unique().astype(str))
postal_code = st.selectbox('Focus on a particular postal code?', postal_codes_options)
if postal_code != 'All':
    interv_subset = interv_subset[interv_subset['Postal Code'] == postal_code]
    travel_time = interv_subset['TravelTime_Destination_minutes'].mean()
else:
    travel_time = interv_subset['TravelTime_Destination_minutes'].mean()

# --- Metrics ----------------------------------------------------------------

col1, col2 = st.columns(2)
with col1:
    centered_metric("Total number of interventions:", interv_subset.shape[0])
    centered_metric("Total number of fatalities:", interv_subset[interv_subset['Dead'] == 'Yes'].shape[0])
with col2:
    centered_metric("Percentage of fatalities:", f"{round((interv_subset[interv_subset['Dead'] == 'Yes'].shape[0] / interv_subset.shape[0]) * 100, 2)}%")
    centered_metric("Average arrival time:", f"{round(travel_time, 2)} minutes")

# --- Map --------------------------------------------------------------------

hotspot_scripts = get_hotspot_layer_html(interv_subset.to_json(date_format='iso'))
map_html = build_final_map_html(hotspot_scripts)

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.components.v1.html(map_html, width=700, height=800)
st.markdown("</div>", unsafe_allow_html=True)

# --- Summary table ----------------------------------------------------------

criteria = st.selectbox('Order variable:', ('Pct Fatality', 'Fatalities', 'Interventions'))

total_interventions = interv_subset.groupby('Postal Code').size().reset_index(name='Interventions')
total_fatal = interv_subset[interv_subset['Dead'] == 'Yes'].groupby('Postal Code').size().reset_index(name='Fatalities')
df = pd.merge(total_interventions, total_fatal, on='Postal Code', how='left')
df['Fatalities'] = df['Fatalities'].fillna(0).astype(int)
df['Pct Fatality'] = df.apply(lambda row: (row['Fatalities'] / row['Interventions']) * 100, axis=1)
df = df.sort_values(by=criteria, ascending=False)
df['Pct Fatality'] = df['Pct Fatality'].apply(lambda x: f"{round(x, 2)}%")

st.markdown(
    f"<h3 style='text-align: center;'>Top 5 {criteria} per Postal Code</h3>",
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style='display: flex; justify-content: center;'>
    <div style='width: 50%;'>
    {}
    </div>
    </div>
    """.format(df.head().to_html(index=False)), unsafe_allow_html=True
)
