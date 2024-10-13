#Loading Packages
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import folium
import os
from io import BytesIO
import requests
from utilities import add_marker, add_circle_marker, centered_metric, load_data

# Caching the load_data function to avoid repeated requests
@st.cache_data
def load_data(url, postalcode=0):
    response = requests.get(url)
    file_stream = BytesIO(response.content)
    if postalcode == 0:
        return pd.read_excel(file_stream, engine='openpyxl')
    else:
        return pd.read_excel(file_stream, engine='openpyxl', dtype={'Postal Code': 'str'})

# Loading Data
links = [
    "https://drive.google.com/uc?id=1x4Ph_EfAo1994I4JVrGwPDmi0y-Vtt0q&export=download",
    "https://drive.google.com/uc?id=19i47foVILPjmA4RyKP4WEBQFXSEvLyEe&export=download",
    "https://drive.google.com/uc?id=12UFMCiZhiIhau1dNUBUdPaOm_KBGVOhw&export=download",
]

hotspots = load_data(links[0], postalcode=1)
greenspots = load_data(links[1], postalcode=0)
bluespots = load_data(links[2], postalcode=0)

# Caching map creation to avoid redundant map generation
@st.cache_data
def create_map():
    brussels_coordinates = [50.8503, 4.3517]
    map_belgium = folium.Map(location=brussels_coordinates, zoom_start=12)
    for _, row in greenspots.iterrows():
        add_marker(row, map_belgium, 'green', 'plus-sign', f"AED: {row['id']}")
    for _, row in bluespots.iterrows():
        add_marker(row, map_belgium, 'blue', 'plus-sign', f"Ambulance: {row['id']}")
    return map_belgium

map_belgium = create_map()

# Display Title
st.markdown(
    """
    <h1 style='text-align: center;'>AED Coverage and Cardiac Arrest Hotspots in Brussels</h1>
    """, unsafe_allow_html=True
)

# User selections options and metrics
intervention_type = st.selectbox('Intervention Criticallity:', ('All', 'Fatal', 'Non-Fatal', 'Critical location'))

if intervention_type == 'Critical location':
    aed_distance = st.number_input('Set critical distance to AED (meters)', min_value=0, value=500)
    ambulance_distance = st.number_input('Set critical distance to Ambulance (meters)', min_value=0, value=3000)
    interv_subset = hotspots.loc[(hotspots['AED_distance'] > aed_distance) & (hotspots['Ambulance_distance'] > ambulance_distance), :]
elif intervention_type == 'Fatal':
    interv_subset = hotspots[hotspots['Dead'] == 'Yes']
elif intervention_type == 'Non-Fatal':
    interv_subset = hotspots[hotspots['Dead'] == 'No']
else:
    interv_subset = hotspots

# Event code selection
event_codes_options = ['All'] + sorted(interv_subset['Event Code'].unique().astype(str))
event_code = st.selectbox('Event code:', event_codes_options)
if event_code != 'All':
    interv_subset = interv_subset[interv_subset['Event Code'] == event_code]

# Postal code selection
postal_codes_options = ['All'] + sorted(interv_subset['Postal Code'].unique().astype(str))
postal_code = st.selectbox('Focus on a particular postal code?', postal_codes_options)
if postal_code != 'All':
    interv_subset = interv_subset[interv_subset['Postal Code'] == postal_code]
    travel_time = interv_subset['TravelTime_Destination_minutes'].mean()
else:
    travel_time = interv_subset['TravelTime_Destination_minutes'].mean()

# Displaying metrics using columns
col1, col2 = st.columns(2)
with col1:
    centered_metric("Total number of interventions:", interv_subset.shape[0])
    centered_metric("Total number of fatalities:", interv_subset[interv_subset['Dead'] == 'Yes'].shape[0])
with col2:
    centered_metric("Percentage of fatalities:", f"{round((interv_subset[interv_subset['Dead'] == 'Yes'].shape[0]/interv_subset.shape[0])*100, 2)}%")
    centered_metric("Average arrival time:", f"{round(travel_time, 2)} minutes")

# Add colored markers for events on the map
interv_subset['Event Code factor'] = pd.factorize(interv_subset['Event Code'])[0]
num_events = interv_subset['Event Code factor'].nunique()
colormap = plt.get_cmap('Set1', num_events)
event_colors = [colors.rgb2hex(colormap(i % colormap.N)) for i in range(num_events)]

for _, row in interv_subset.iterrows():
    event_color = event_colors[row['Event Code factor']]
    add_circle_marker(row, map_belgium, event_color)

# Save and display the map
dir = os.getcwd()
mappath = os.path.join(dir, 'map_belgium.html')
map_belgium.save(mappath)
map_html = open(mappath, 'r').read()

st.markdown(
    """
    <div style='text-align: center;'>
    """, unsafe_allow_html=True
)

st.components.v1.html(map_html, width=700, height=800)

st.markdown(
    """
    </div>
    """, unsafe_allow_html=True
)

# Displaying sorted fatalities data
criteria = st.selectbox('Order variable:', ('Pct Fatality', 'Fatalities', 'Interventions'))
total_interventions = interv_subset.groupby('Postal Code').size().reset_index(name='Interventions')
total_fatal = interv_subset[interv_subset['Dead'] == 'Yes'].groupby('Postal Code').size().reset_index(name='Fatalities')
df = pd.merge(total_interventions, total_fatal, on='Postal Code', how='left')
df['Fatalities'] = df['Fatalities'].fillna(0).astype(int)
df['Pct Fatality'] = df.apply(lambda row: (row['Fatalities'] / row['Interventions']) * 100, axis=1)
df = df.sort_values(by=criteria, ascending=False)
df['Pct Fatality'] = df['Pct Fatality'].apply(lambda x: f"{round(x, 2)}%")

st.markdown(
    f"""
    <h3 style='text-align: center;'>Top 5 {criteria} per Postal Code</h3>
    """, unsafe_allow_html=True
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
