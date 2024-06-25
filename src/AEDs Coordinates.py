#Loading Packages
import pandas as pd
import numpy as np
import gdown
from geopy.geocoders import Nominatim
from utilities import geocode_address

#Loading Data
links = [
    "https://drive.google.com/file/d/14wjMY2t2EVGCVfu-iVqgomgtUPH9dYLb/view?usp=drive_link"
]

#Downloading data
file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]
gdown.download(urls[0], 'aed_locations.parquet.gzip', quiet=False)
aed = pd.read_parquet(f'aed_locations.parquet.gzip')

#AEDs Cleaning
aed = aed.dropna(subset=['address','number','postal_code'])
aed[['number','postal_code']] = aed[['number','postal_code']].astype(int).astype(str)
aed['Full_adress'] = aed.apply(lambda row: f"{row['address']} {row['number']}, {row['postal_code']}", axis=1)
outpath='C:/Users/oriol/OneDrive/UNI/MASTER/Modern Data Analytics/Project/data/' #New path needs to be specified
aed['Full_adress'].to_csv(f'{outpath}adresses.csv', index=False)
aed[['latitude', 'longitude']] = aed.apply(geocode_address, axis=1)
print(aed.head())