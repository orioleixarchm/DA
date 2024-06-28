#Loading Packages
import numpy as np
import pandas as pd
import gdown
import os
from sklearn.cluster import DBSCAN

#Using 18 logical cores
os.environ['LOKY_MAX_CPU_COUNT'] = '18'

#Loading Data
links = [
    "https://drive.google.com/file/d/1Yl4X_f_IifkV5OpWgylU_bI3i2Fmnazs/edit?usp=drive_link",
    "https://drive.google.com/file/d/1FMc9Cgx77JaCryQorZhtwoNJrBJkNefc/edit?usp=drive_link",
    "https://drive.google.com/file/d/1_6ppcCg0q2p6A9LKzbW057-y-mYb5HYk/edit?usp=drive_link"
]

#Downloading data
dir = os.getcwd()
file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]
gdown.download(urls[0], os.path.join(dir,'interventions.xlsx'), quiet=False)
gdown.download(urls[1], os.path.join(dir,'ambulances.xlsx'), quiet=False)
gdown.download(urls[2], os.path.join(dir,'aed.xlsx'), quiet=False)
interventions = pd.read_excel(os.path.join(dir,'interventions.xlsx'))
ambulances = pd.read_excel(os.path.join(dir,'ambulances.xlsx'))
aed = pd.read_excel(os.path.join(dir,'aed.xlsx'))

#Loading AED data (locally)
#dir = os.getcwd()
#interventionpath = os.path.join(dir,'interventions.xlsx')
#ambulancespath = os.path.join(dir,'ambulances.xlsx')
#aedpath = os.path.join(dir,'aed.xlsx')
#interventions = pd.read_excel(interventionpath)
#ambulances = pd.read_excel(ambulancespath)
#aed = pd.read_excel(aedpath)

#DBSCAN clustering with Haversine distance metric for interventions
intervention_rad = np.radians(interventions[['Longitude','Latitude']])
Clustering_interv = DBSCAN(eps=0.000008 , min_samples=5, metric='haversine').fit(intervention_rad) #50 metres area
labels = Clustering_interv.labels_ #Numbering clusters
interventions['Cluster'] = labels 
hotspots = interventions[interventions['Cluster'] != -1] #Removing noise (label = -1)

#Display the hotspots
print('Hotspot data frame:\n',hotspots.head())
print('\nObservation per cluster:\n',hotspots['Cluster'].value_counts())
print('\nTotal number of clusters:\n',len(hotspots['Cluster'].value_counts()))

#DBSCAN clustering with Haversine distance metric for AEDs placement
aed_rad = np.radians(aed[['Longitude','Latitude']])
Clustering_aed = DBSCAN(eps=0.000015 , min_samples=5, metric='haversine').fit(aed_rad) #100 metres area
labels = Clustering_aed.labels_ #Numbering clusters
aed['Cluster'] = labels 
greenspots = aed

#Display the Greenspots
print('Greenspot data frame:\n',greenspots.head())
print('\nObservation per cluster:\n',greenspots['Cluster'].value_counts())
print('\nTotal number of clusters:\n',len(greenspots['Cluster'].value_counts()))

#DBSCAN clustering with Haversine distance metric for Ambulances
ambulances_rad = np.radians(ambulances[['Longitude','Latitude']])
Clustering_ambulances = DBSCAN(eps=0.0008 , min_samples=2, metric='haversine').fit(ambulances_rad) #5000 metres area
labels = Clustering_ambulances.labels_ #Numbering clusters
ambulances['Cluster'] = labels 
bluespots = ambulances[ambulances['Cluster'] != -1] #Removing noise (label = -1)

#Display the Bluespots
print('Bluespots data frame:\n',bluespots.head())
print('\nObservation per cluster:\n',bluespots['Cluster'].value_counts())
print('\nTotal number of clusters:\n',len(bluespots['Cluster'].value_counts()))

#Exporting to excel
dir = os.getcwd()
interventions.to_excel(os.path.join(dir,'hotspots.xlsx'), index=False)
aed.to_excel(os.path.join(dir,'greenspots.xlsx'), index=False)
ambulances.to_excel(os.path.join(dir,'bluespots.xlsx'), index=False)




