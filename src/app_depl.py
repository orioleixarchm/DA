# Loading Packages
import json
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import folium
from folium import GeoJson
import requests
from io import BytesIO
from utilities import add_marker, add_circle_marker, centered_metric

# ---------------------------------------------------------------------------
# Data loading  (cached – runs once per session, not on every filter change)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Loading data…")
def load_data(url, postalcode=0):
    response = requests.get(url)
    file_stream = BytesIO(response.content)
    if postalcode == 1:
        return pd.read_excel(file_stream, engine='openpyxl', dtype={'Postal Code': 'str'})
    return pd.read_excel(file_stream, engine='openpyxl')


links = [
    "https://drive.google.com/uc?id=1x4Ph_EfAo1994I4JVrGwPDmi0y-Vtt0q&export=download",
    "https://drive.google.com/uc?id=19i47foVILPjmA4RyKP4WEBQFXSEvLyEe&export=download",
    "https://drive.google.com/uc?id=12UFMCiZhiIhau1dNUBUdPaOm_KBGVOhw&export=download",
]

hotspots   = load_data(links[0], postalcode=1)
greenspots = load_data(links[1])
bluespots  = load_data(links[2])


# ---------------------------------------------------------------------------
# Base map  (cached – AED + ambulance markers never change)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Building base map…")
def get_base_map_html():
    """
    Build the static layer (AED + ambulance markers) once and cache the HTML.
    Returns the raw HTML string so we can inject the dynamic GeoJSON later
    via a tiny <script> snippet.
    """
    brussels_coordinates = [50.8503, 4.3517]
    m = folium.Map(location=brussels_coordinates, zoom_start=12)

    for _, row in greenspots.iterrows():
        add_marker(row, m, 'green', 'plus-sign', f"AED: {row['id']}")
    for _, row in bluespots.iterrows():
        add_marker(row, m, 'blue', 'plus-sign', f"Ambulance: {row['id']}")

    return m._repr_html_()


# ---------------------------------------------------------------------------
# GeoJSON helper  (cached per unique filter combination)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def build_geojson(subset_json: str) -> str:
    """
    Convert a JSON-serialised subset of hotspots into a GeoJSON FeatureCollection
    string.  Results are cached, so repeated calls with identical data are free.
    """
    subset = pd.read_json(subset_json, dtype={'Postal Code': 'str'})

    if subset.empty:
        return json.dumps({"type": "FeatureCollection", "features": []})

    # Assign a colour per event code
    subset = subset.copy()
    subset['_code_factor'] = pd.factorize(subset['Event Code'])[0]
    n = subset['_code_factor'].nunique()
    cmap = plt.get_cmap('Set1', n)
    code_to_color = {
        i: colors.rgb2hex(cmap(i % cmap.N)) for i in range(n)
    }

    features = []
    for _, row in subset.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['Longitude'], row['Latitude']],
            },
            "properties": {
                "color":              code_to_color[row['_code_factor']],
                "Event Code":         str(row['Event Code']),
                "AED_distance":       round(float(row['AED_distance']), 1) if pd.notna(row.get('AED_distance')) else "N/A",
                "Ambulance_distance": round(float(row['Ambulance_distance']), 1) if pd.notna(row.get('Ambulance_distance')) else "N/A",
                "Dead":               str(row['Dead']),
            },
        })

    return json.dumps({"type": "FeatureCollection", "features": features})


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.markdown(
    "<h1 style='text-align:center;'>AED Coverage and Cardiac Arrest Hotspots in Brussels</h1>",
    unsafe_allow_html=True,
)

# --- Filters ----------------------------------------------------------------

intervention_type = st.selectbox(
    'Intervention Criticality:',
    ('All', 'Fatal', 'Non-Fatal', 'Critical location'),
)

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

# --- Metrics ----------------------------------------------------------------

travel_time  = interv_subset['TravelTime_Destination_minutes'].mean()
n_total      = interv_subset.shape[0]
n_fatal      = interv_subset[interv_subset['Dead'] == 'Yes'].shape[0]
pct_fatal    = (n_fatal / n_total * 100) if n_total > 0 else 0.0

col1, col2 = st.columns(2)
with col1:
    centered_metric("Total number of interventions:", n_total)
    centered_metric("Total number of fatalities:",    n_fatal)
with col2:
    centered_metric("Percentage of fatalities:",  f"{round(pct_fatal, 2)}%")
    centered_metric("Average arrival time:",      f"{round(travel_time, 2)} minutes")

# --- Map --------------------------------------------------------------------
# Strategy:
#   1. Render the cached base map (static AED/ambulance markers).
#   2. Inject a <script> that replaces the empty GeoJSON layer with the
#      current filter's GeoJSON – no Python-side map rebuild required.

base_html   = get_base_map_html()
geojson_str = build_geojson(interv_subset.to_json(date_format='iso'))

# Extract Folium's generated map variable name (e.g. "map_a3f2b1c4d5e6")
import re
map_var_match = re.search(r'var (map_[a-f0-9]+)\s*=\s*L\.map', base_html)
map_var = map_var_match.group(1) if map_var_match else "map"

inject_script = f"""
<script>
(function() {{
  function injectLayer() {{
    if (typeof {map_var} === 'undefined') {{
      setTimeout(injectLayer, 100);
      return;
    }}
    var geojson = {geojson_str};
    L.geoJSON(geojson, {{
      pointToLayer: function(feature, latlng) {{
        return L.circleMarker(latlng, {{
          radius: 5,
          fillColor: feature.properties.color,
          color:     feature.properties.color,
          weight: 1,
          fillOpacity: 0.8
        }});
      }},
      onEachFeature: function(feature, layer) {{
        var p = feature.properties;
        layer.bindPopup(
          "<b>Event:</b> "        + p["Event Code"]         + "<br>" +
          "<b>AED dist (m):</b> " + p["AED_distance"]       + "<br>" +
          "<b>Amb dist (m):</b> " + p["Ambulance_distance"] + "<br>" +
          "<b>Fatal:</b> "        + p["Dead"]
        );
      }}
    }}).addTo({map_var});
  }}
  if (document.readyState === 'complete') {{
    injectLayer();
  }} else {{
    window.addEventListener('load', injectLayer);
  }}
}})();
</script>
"""

full_html = base_html.replace("</body>", inject_script + "</body>")

st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.components.v1.html(full_html, width=700, height=800)
st.markdown("</div>", unsafe_allow_html=True)

# --- Summary table ----------------------------------------------------------

criteria = st.selectbox('Order variable:', ('Pct Fatality', 'Fatalities', 'Interventions'))

total_interventions = interv_subset.groupby('Postal Code').size().reset_index(name='Interventions')
total_fatal_df      = interv_subset[interv_subset['Dead'] == 'Yes'].groupby('Postal Code').size().reset_index(name='Fatalities')
df = pd.merge(total_interventions, total_fatal_df, on='Postal Code', how='left')
df['Fatalities']   = df['Fatalities'].fillna(0).astype(int)
df['Pct Fatality'] = df.apply(lambda r: (r['Fatalities'] / r['Interventions']) * 100, axis=1)
df = df.sort_values(by=criteria, ascending=False)
df['Pct Fatality'] = df['Pct Fatality'].apply(lambda x: f"{round(x, 2)}%")

st.markdown(
    f"<h3 style='text-align:center;'>Top 5 {criteria} per Postal Code</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='display:flex;justify-content:center;'>"
    "<div style='width:50%;'>{}</div></div>".format(df.head().to_html(index=False)),
    unsafe_allow_html=True,
)
