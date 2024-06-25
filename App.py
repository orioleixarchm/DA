#Loading Packages
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import folium
import os
import gdown
from utilities import add_marker, add_circle_marker

#Using 18 logical cores
os.environ['LOKY_MAX_CPU_COUNT'] = '18'

#Loading Data
links = [
    "https://drive.google.com/file/d/1iZ6Cpzh4iniSv5D6firXnaWXAI5DCw3A/edit?usp=drive_link",
    "https://drive.google.com/file/d/19i47foVILPjmA4RyKP4WEBQFXSEvLyEe/edit?usp=drive_link",
    "https://drive.google.com/file/d/12UFMCiZhiIhau1dNUBUdPaOm_KBGVOhw/edit?usp=drive_link"
]

#Downloading data
file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]
gdown.download(urls[0], 'hotspots_distance.xlsx', quiet=False)
gdown.download(urls[1], 'greenspots.xlsx', quiet=False)
gdown.download(urls[2], 'bluespots.xlsx', quiet=False)
hotspots = pd.read_excel(f'hotspots_distance.xlsx', dtype={'Postal Code': 'str','AED_distance': 'int','Ambulance_distance': 'int'})
greenspots = pd.read_excel(f'greenspots.xlsx', dtype={'Cluster': 'int','id':'str'})
bluespots = pd.read_excel(f'bluespots.xlsx', dtype={'Cluster': 'int','id':'str'})

#Area of Brussels region
brussels_coordinates = [50.8503, 4.3517]
map_belgium = folium.Map(location=brussels_coordinates, zoom_start=12)

#Adding user selections options
intervention_type = st.selectbox('Intervention outcome degree of severity', ('All', 'Fatal', 'Non-Fatal', 'Critical location'))
if intervention_type == 'Critical location':
    aed_distance = st.number_input('Set critical distance to AED (meters)', min_value=0, value=500)
    ambulance_distance = st.number_input('Set critical distance to Ambulance (meters)', min_value=0, value=3000)
    hotspots['Critical location'] = np.where((hotspots['AED_distance'] > aed_distance) & (hotspots['Ambulance_distance'] > ambulance_distance), 'Yes', 'No')
    interv_subset = hotspots[hotspots['Critical location'] == 'Yes']
elif intervention_type == 'Fatal':
    interv_subset = hotspots[hotspots['Dead'] == 'Yes']
elif intervention_type == 'Non-Fatal':
    interv_subset = hotspots[hotspots['Dead'] == 'No']
else:
    interv_subset = hotspots

postal_codes_options = ['All'] + sorted(interv_subset['Postal Code'].unique().astype(str))
postal_code = st.selectbox('Focus on a particular postal code?', (postal_codes_options))
if postal_code != 'All':
    interv_subset = interv_subset[interv_subset['Postal Code'] == postal_code]

interv_subset['Cluster'] = pd.factorize(interv_subset['Cluster'])[0]

#Adding Ambulances and AEDs to the map
for _, row in greenspots.iterrows():
    add_marker(row, map_belgium, 'green', 'plus-sign', f"AED: {row['id']}")

for _, row in bluespots.iterrows():
    add_marker(row, map_belgium, 'blue', 'plus-sign', f"Ambulance: {row['id']}")

num_clusters = interv_subset['Cluster'].nunique()
colormap = plt.get_cmap('Set1', num_clusters)
cluster_colors = [colors.rgb2hex(colormap(i % colormap.N)) for i in range(num_clusters)]

#Adding intervention hotspots to the map
for _, row in interv_subset.iterrows():
    cluster_color = cluster_colors[row['Cluster']]
    add_circle_marker(row, map_belgium, cluster_color)

# Loading the map
map_belgium.save('C:/Users/oriol/OneDrive/UNI/MASTER/Modern Data Analytics/Project/Dev 1/map_belgium.html')
map_html = open('C:/Users/oriol/OneDrive/UNI/MASTER/Modern Data Analytics/Project/Dev 1/map_belgium.html', 'r').read()
st.title('AED Coverage and Cardiac Arrest Hotspots in Brussels')
st.components.v1.html(map_html, height=600)

#Run in terminal by "python -m streamlit run App.py"