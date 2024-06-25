#Loading Packages
import numpy as np
import pandas as pd
import gdown
import os
from utilities import distance_interv_aed, distance_interv_amb
from scipy.spatial import KDTree
from geopy.distance import geodesic

#Using 18 logical cores
os.environ['LOKY_MAX_CPU_COUNT'] = '18'

#Loading Data
links = [
    "https://drive.google.com/file/d/1meuUUiUbCNDhhCvWTrs68gRgQ5qYQGcG/edit?usp=drive_link",
    "https://drive.google.com/file/d/19i47foVILPjmA4RyKP4WEBQFXSEvLyEe/edit?usp=drive_link",
    "https://drive.google.com/file/d/12UFMCiZhiIhau1dNUBUdPaOm_KBGVOhw/edit?usp=drive_link"
]

#Downloading data
file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]
gdown.download(urls[0], 'hotspots.xlsx', quiet=False)
gdown.download(urls[1], 'greenspots.xlsx', quiet=False)
gdown.download(urls[2], 'bluespots.xlsx', quiet=False)
hotspots = pd.read_excel(f'hotspots.xlsx')
greenspots = pd.read_excel(f'greenspots.xlsx')
bluespots = pd.read_excel(f'bluespots.xlsx')

#Creating K-d treea
aed_matrix = greenspots[['Latitude', 'Longitude']].values
ambulances_matrix = bluespots[['Latitude', 'Longitude']].values
aed_tree = KDTree(aed_matrix)
amb_tree = KDTree(ambulances_matrix)

#Distances from intervention clusters to the closest aed cluster
hotspots['AED_distance'] = hotspots.apply(lambda row: distance_interv_aed(row, aed_tree, aed_matrix), axis=1)
hotspots['Ambulance_distance'] = hotspots.apply(lambda row: distance_interv_amb(row, amb_tree, ambulances_matrix), axis=1)
hotspots.dropna(subset=['AED_distance','Ambulance_distance'], inplace=True)
hotspots['Postal Code'] = hotspots['Postal Code'].astype(int).astype(str)
hotspots['AED_distance'] = round(hotspots['AED_distance'],0).astype(int)
hotspots['Ambulance_distance'] = round(hotspots['Ambulance_distance'],0).astype(int)

#Hotspots with distances
print(hotspots.head())
print(hotspots.tail())
print(hotspots.shape)

#Exporting to excel
outpath='C:/Users/oriol/OneDrive/UNI/MASTER/Modern Data Analytics/Project/data/' #New path needs to be specified
hotspots.to_excel(f'{outpath}hotspots_distance.xlsx', index=False)