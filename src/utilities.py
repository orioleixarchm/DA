"""
Utility functions for the project.

This module contains reusable functions data processing,
and visualization used across different parts of the project.
"""

#Loading Packages
import pandas as pd
import numpy as np
import gdown
from geopy.geocoders import Nominatim
from sklearn.cluster import DBSCAN
import os
from scipy.spatial import KDTree
from geopy.distance import geodesic
import streamlit as st
import folium
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt

#Reusable functions
def geocode_address(row):
    location = geolocator.geocode(row['Full_adress'])
    if location:
        return pd.Series([location.latitude, location.longitude])
    else:
        return pd.Series([None, None])
    
def distance_interv_aed(row,aed_tree,aed_matrix):
    dist, idx = aed_tree.query([row['Latitude'], row['Longitude']])
    nearest_aed = aed_matrix[idx]
    distance_aed = geodesic((row['Latitude'], row['Longitude']), nearest_aed).meters
    return distance_aed

def distance_interv_amb(row,amb_tree,ambulances_matrix):
    dist, idx = amb_tree.query([row['Latitude'], row['Longitude']])
    nearest_amb = ambulances_matrix[idx]
    distance_amb = geodesic((row['Latitude'], row['Longitude']), nearest_amb).meters
    return distance_amb 

def add_marker(row, map_obj, color, icon, popup_text):
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_text,
        icon=folium.Icon(color=color, icon=icon)
    ).add_to(map_obj)

def add_circle_marker(row, map_obj, color):
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        popup=f"Hotspot: {row['Event Code']}<br>AED Distance: {row['AED_distance']} meters<br>Ambulance Distance: {row['Ambulance_distance']} meters<br>Fatal: {row['Dead']}"
    ).add_to(map_obj)