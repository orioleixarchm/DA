"""
Utility functions for the project.

This module contains the functions mainly used for coordinate and distance computations,
as well as the ones used for visualization at the app development within the project.
"""

#Loading Packages
import pandas as pd
from geopy.distance import geodesic
import folium

#Returns the coordinates for a given full address.
def geocode_address(row):
    location = geolocator.geocode(row['Full_adress'])
    if location:
        return pd.Series([location.latitude, location.longitude])
    else:
        return pd.Series([None, None])
        
#Identifies the closest aed to a given set fo coordinates and returns the distance in meters to it from that given coordinates.   
def distance_interv_aed(row,aed_tree,aed_matrix):
    dist, idx = aed_tree.query([row['Latitude'], row['Longitude']])
    nearest_aed = aed_matrix[idx]
    distance_aed = geodesic((row['Latitude'], row['Longitude']), nearest_aed).meters
    return distance_aed

#Identifies the closest ambulance center to a given set fo coordinates and returns the distance in meters to it from that given coordinates.   
def distance_interv_amb(row,amb_tree,ambulances_matrix):
    dist, idx = amb_tree.query([row['Latitude'], row['Longitude']])
    nearest_amb = ambulances_matrix[idx]
    distance_amb = geodesic((row['Latitude'], row['Longitude']), nearest_amb).meters
    return distance_amb 

#Adds location markers (specifying the kind of symbol and color displayed) at given coordinates in a map.   
def add_marker(row, map_obj, color, icon, popup_text):
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_text,
        icon=folium.Icon(color=color, icon=icon)
    ).add_to(map_obj)

#Adds circular markers (specifying the kind of symbol and color displayed) at given coordinates in a map.   
def add_circle_marker(row, map_obj, color):
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        popup=f"Hotspot: {row['Event Code']}<br>AED Distance: {row['AED_distance']} meters<br>Ambulance Distance: {row['Ambulance_distance']} meters<br>Fatal: {row['Dead']}"
    ).add_to(map_obj)
