# Loading Packages
import copy
import json
import re
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import folium
import requests
from io import BytesIO
from utilities import add_marker, centered_metric

# ---------------------------------------------------------------------------
# Data loading — cached, runs once per session
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
# Build a GeoJSON FeatureCollection for the hotspot subset
# Cached per unique filter combination — instant on repeat calls
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def build_hotspot_geojson(subset_json: str) -> str:
    subset = pd.read_json(subset_json, dtype={'Postal Code': 'str'})

    if subset.empty:
        return json.dumps({"type": "FeatureCollection", "features": []})

    subset = subset.copy()
    subset['_code_factor'] = pd.factorize(subset['Event Code'])[0]
    n = subset['_code_factor'].nunique()
    cmap = plt.get_cmap('Set1', n)
    code_to_color = {i: colors.rgb2hex(cmap(i % cmap.N)) for i in range(n)}

    features = []
    for _, row in subset.iterrows():
        aed_dist = round(float(row['AED_distance']), 1) if pd.notna(row.get('AED_distance')) else "N/A"
        amb_dist = round(float(row['Ambulance_distance']), 1) if pd.notna(row.get('Ambulance_distance')) else "N/A"
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['Longitude']), float(row['Latitude'])],
            },
            "properties": {
                "color":              code_to_color[row['_code_factor']],
                "Event Code":         str(row['Event Code']),
                "AED_distance":       aed_dist,
                "Ambulance_distance": amb_dist,
                "Dead":               str(row['Dead']),
            },
        })

    return json.dumps({"type": "FeatureCollection", "features": features})


# ---------------------------------------------------------------------------
# Base map HTML — AED + ambulance markers, cached once per session
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Building base map…")
def get_base_map_html() -> str:
    m = folium.Map(location=[50.8503, 4.3517], zoom_start=12)
    for _, row in greenspots.iterrows():
        add_marker(row, m, 'green', 'plus-sign', f"AED: {row['id']}")
    for _, row in bluespots.iterrows():
        add_marker(row, m, 'blue', 'plus-sign', f"Ambulance: {row['id']}")
    return m._repr_html_()


def build_full_map_html(geojson_str: str) -> str:
    base_html = get_base_map_html()

    # Folium generates:  var map_XXXX = L.map(...)
    # We need that variable name to call .addTo() on it from our injected script.
    match = re.search(r'var\s+(map_[a-zA-Z0-9_]+)\s*=\s*L\.map\(', base_html)

    if not match:
        # Regex failed — safe fallback: rebuild everything the slow way
        m = folium.Map(location=[50.8503, 4.3517], zoom_start=12)
        for _, row in greenspots.iterrows():
            add_marker(row, m, 'green', 'plus-sign', f"AED: {row['id']}")
        for _, row in bluespots.iterrows():
            add_marker(row, m, 'blue', 'plus-sign', f"Ambulance: {row['id']}")
        geojson = json.loads(geojson_str)
        for feature in geojson["features"]:
            lon, lat = feature["geometry"]["coordinates"]
            p = feature["properties"]
            folium.CircleMarker(
                location=[lat, lon], radius=5,
                color=p["color"], fill=True, fill_color=p["color"],
                popup=(f"Event: {p['Event Code']}<br>AED: {p['AED_distance']} m<br>"
                       f"Ambulance: {p['Ambulance_distance']} m<br>Fatal: {p['Dead']}"),
            ).add_to(m)
        return m._repr_html_()

    map_var = match.group(1)

    # Inject a script that waits for Leaflet to finish initialising,
    # then adds a GeoJSON layer with circle markers for the hotspots.
    script = f"""
<script>
(function waitForMap() {{
  if (typeof window["{map_var}"] === "undefined") {{
    setTimeout(waitForMap, 50);
    return;
  }}
  var _map = window["{map_var}"];
  var geojson = {geojson_str};
  L.geoJSON(geojson, {{
    pointToLayer: function(feature, latlng) {{
      return L.circleMarker(latlng, {{
        radius: 5,
        fillColor: feature.properties.color,
        color:     feature.properties.color,
        weight: 1,
        opacity: 1,
        fillOpacity: 0.85
      }});
    }},
    onEachFeature: function(feature, layer) {{
      var p = feature.properties;
      layer.bindPopup(
        "<b>Event:</b> "         + p["Event Code"]         + "<br>" +
        "<b>AED (m):</b> "       + p["AED_distance"]       + "<br>" +
        "<b>Ambulance (m):</b> " + p["Ambulance_distance"] + "<br>" +
        "<b>Fatal:</b> "         + p["Dead"]
      );
    }}
  }}).addTo(_map);
}})();
</script>
"""
    return base_html.replace("</body>", script + "\n</body>")


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
    aed_dist_thresh = st.number_input('Set critical distance to AED (meters)',       min_value=0, value=500)
    amb_dist_thresh = st.number_input('Set critical distance to Ambulance (meters)', min_value=0, value=3000)
    interv_subset = hotspots.loc[
        (hotspots['AED_distance'] > aed_dist_thresh) &
        (hotspots['Ambulance_distance'] > amb_dist_thresh)
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

n_total     = interv_subset.shape[0]
n_fatal     = interv_subset[interv_subset['Dead'] == 'Yes'].shape[0]
pct_fatal   = (n_fatal / n_total * 100) if n_total > 0 else 0.0
travel_time = interv_subset['TravelTime_Destination_minutes'].mean()

col1, col2 = st.columns(2)
with col1:
    centered_metric("Total number of interventions:", n_total)
    centered_metric("Total number of fatalities:",    n_fatal)
with col2:
    centered_metric("Percentage of fatalities:",  f"{round(pct_fatal, 2)}%")
    centered_metric("Average arrival time:",      f"{round(travel_time, 2)} minutes")

# --- Map --------------------------------------------------------------------

geojson_str = build_hotspot_geojson(interv_subset.to_json(date_format='iso'))
map_html    = build_full_map_html(geojson_str)

st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.components.v1.html(map_html, width=700, height=800)
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
