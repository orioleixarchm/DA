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
from utilities import add_marker, add_circle_marker, centered_metric

#Using 18 logical cores
os.environ['LOKY_MAX_CPU_COUNT'] = '18'

#Loading Data
# links = [
#     "https://drive.google.com/file/d/1x4Ph_EfAo1994I4JVrGwPDmi0y-Vtt0q/edit?usp=drive_link",
#     "https://drive.google.com/file/d/19i47foVILPjmA4RyKP4WEBQFXSEvLyEe/edit?usp=drive_link",
#     "https://drive.google.com/file/d/12UFMCiZhiIhau1dNUBUdPaOm_KBGVOhw/edit?usp=drive_link"
# ]

# # #Downloading data
# dir = os.getcwd()
# file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
# urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]
# gdown.download(urls[0], os.path.join(dir,'hotspots_distance.xlsx'), quiet=False)
# gdown.download(urls[1], os.path.join(dir,'greenspots.xlsx'), quiet=False)
# gdown.download(urls[2], os.path.join(dir,'bluespots.xlsx'), quiet=False)
# hotspots = pd.read_excel(os.path.join(dir,'hotspots_distance.xlsx'), dtype={'Postal Code': 'str'})
# greenspots = pd.read_excel(os.path.join(dir,'greenspots.xlsx'), dtype={'Cluster': 'int','id':'str'})
# bluespots = pd.read_excel(os.path.join(dir,'bluespots.xlsx'), dtype={'Cluster': 'int','id':'str'})

#Loading AED data (locally)
dir = os.getcwd()
hotspots = pd.read_excel(os.path.join(dir,'hotspots_distance.xlsx'), dtype={'Postal Code': 'str'})
greenspots = pd.read_excel(os.path.join(dir,'greenspots.xlsx'), dtype={'Cluster': 'int','id':'str'})
bluespots = pd.read_excel(os.path.join(dir,'bluespots.xlsx'), dtype={'Cluster': 'int','id':'str'})

#Area of Brussels region
brussels_coordinates = [50.8503, 4.3517]
map_belgium = folium.Map(location=brussels_coordinates, zoom_start=12)

#Adding title
st.markdown(
    """
    <h1 style='text-align: center;'>AED Coverage and Cardiac Arrest Hotspots in Brussels</h1>
    """,
    unsafe_allow_html=True
)

#Adding user selections options and metrics
intervention_type = st.selectbox('Intervention Criticallity:', ('All', 'Fatal', 'Non-Fatal', 'Critical location'))
if intervention_type == 'Critical location':
    aed_distance = st.number_input('Set critical distance to AED (meters)', min_value=0, value=500)
    ambulance_distance = st.number_input('Set critical distance to Ambulance (meters)', min_value=0, value=3000)
    interv_subset = hotspots.loc[(hotspots['AED_distance'] > aed_distance) & (hotspots['Ambulance_distance'] > ambulance_distance),:]
elif intervention_type == 'Fatal':
    interv_subset = hotspots[hotspots['Dead'] == 'Yes']
elif intervention_type == 'Non-Fatal':
    interv_subset = hotspots[hotspots['Dead'] == 'No']
else:
    interv_subset = hotspots

event_codes_options = ['All'] + sorted(interv_subset['Event Code'].unique().astype(str))
event_code = st.selectbox('Event code:', (event_codes_options))
if event_code != 'All':
    interv_subset = interv_subset[interv_subset['Event Code'] == event_code]

postal_codes_options = ['All'] + sorted(interv_subset['Postal Code'].unique().astype(str))
postal_code = st.selectbox('Focus on a particular postal code?', (postal_codes_options))
if postal_code != 'All':
    interv_subset = interv_subset[interv_subset['Postal Code'] == postal_code]
    travel_time = interv_subset['TravelTime_Destination_minutes'].mean()
else:
    travel_time = interv_subset['TravelTime_Destination_minutes'].mean()

col1, col2 = st.columns(2)
with col1:
    centered_metric("Total number of interventions:", interv_subset.shape[0])
    centered_metric("Total number of fatalities:", interv_subset[interv_subset['Dead'] == 'Yes'].shape[0])
with col2:
    centered_metric("Percentage of fatalities:", f"{round((interv_subset[interv_subset['Dead'] == 'Yes'].shape[0]/interv_subset.shape[0])*100,2)}%")
    centered_metric("Average arrival time:", f"{round(travel_time,2)} minutes")

#Adding Ambulances and AEDs to the map
for _, row in greenspots.iterrows():
    add_marker(row, map_belgium, 'green', 'plus-sign', f"AED: {row['id']}")

for _, row in bluespots.iterrows():
    add_marker(row, map_belgium, 'blue', 'plus-sign', f"Ambulance: {row['id']}")

interv_subset['Cluster'] = pd.factorize(interv_subset['Cluster'])[0]
num_clusters = interv_subset['Cluster'].nunique()
colormap = plt.get_cmap('Set1', num_clusters)
cluster_colors = [colors.rgb2hex(colormap(i % colormap.N)) for i in range(num_clusters)]

#Adding intervention hotspots to the map
for _, row in interv_subset.iterrows():
    cluster_color = cluster_colors[row['Cluster']]
    add_circle_marker(row, map_belgium, cluster_color)

# Loading the map
dir = os.getcwd()
mappath = os.path.join(dir,'map_belgium.html')
map_belgium.save(mappath)
map_html = open(mappath, 'r').read()
st.markdown(
    """
    <div style='text-align: center;'>
    """,
    unsafe_allow_html=True
)

st.components.v1.html(map_html, width=700, height=800)

st.markdown(
    """
    </div>
    """,
    unsafe_allow_html=True
)

#Adding Fatalities data frame
criteria = st.selectbox('Order varible:', ('Pct Fatality', 'Fatalities', 'Interventions'))
total_interventions = interv_subset.groupby('Postal Code').size().reset_index(name='Interventions')
total_fatal = interv_subset[interv_subset['Dead'] == 'Yes'].groupby('Postal Code').size().reset_index(name='Fatalities')
df = pd.merge(total_interventions,total_fatal, on='Postal Code', how='left')
df['Fatalities'] = df['Fatalities'].fillna(0).astype(int)
df['Pct Fatality'] = df.apply(lambda row: f"{round((row['Fatalities']/row['Interventions'])*100,2)}%",axis=1)
df = df.sort_values(by=criteria, ascending=False)

st.markdown(
    f"""
    <h3 style='text-align: center;'>Top 5 {criteria} per Postal Code</h3>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style='display: flex; justify-content: center;'>
        <div style='width: 50%;'>
            {}
        </div>
    </div>
    """.format(df.head().to_html(index=False)),
    unsafe_allow_html=True
)
