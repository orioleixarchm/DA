#Loading Packages
import pandas as pd
import numpy as np
import gdown
import os

#Loading Data
links = [
    "https://drive.google.com/file/d/1VYm1Bs3I3k8BgZGPC_D0k0JEhPJzBKqJ/edit?usp=drive_link",
    "https://drive.google.com/file/d/1p0SIbiNYHE454hc4PSWH6E5dYycY36_K/edit?usp=drive_link",
    "https://drive.google.com/file/d/1vCBExpQ9N7-X084u3R55A_UxB0qao1Hx/edit?usp=drive_link",
    "https://drive.google.com/file/d/1uO1av0mAJtgUEj0Rb_4nFm1GMSmyUMjM/edit?usp=drive_link"
]

#Downloading data
dir = os.getcwd()
file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]
gdown.download(urls[0], os.path.join(dir,'intervb1.parquet.gzip'), quiet=False)
gdown.download(urls[1], os.path.join(dir,'intervb2.parquet.gzip'), quiet=False)
gdown.download(urls[2], os.path.join(dir,'ambulances.parquet.gzip'), quiet=False)
gdown.download(urls[3], os.path.join(dir,'aed.xlsx'), quiet=False)
intervb1 = pd.read_parquet(os.path.join(dir,'intervb1.parquet.gzip'))
intervb2 = pd.read_parquet(os.path.join(dir,'intervb2.parquet.gzip'))
ambulances = pd.read_parquet(os.path.join(dir,'ambulances.parquet.gzip'))
aed = pd.read_excel(os.path.join(dir,'aed.xlsx'), dtype={'id':'str'})

#Loading AED data (locally)
#dir = os.getcwd()
#aed = pd.read_excel(os.path.join(dir,'aed_coord.xlsx'), dtype={'id':'str'})

#Interventions cleaning
intervb1['Event Code'] = intervb1['eventtype_firstcall'].str.split().str[0]
intervb2['Event Code'] = intervb2['EventType and EventLevel'].str.split().str[0]

intervb1['Postal Code'] = intervb1['postalcode_intervention']
intervb2['Postal Code'] = intervb2['Cityname Intervention'].str.split().str[0].apply(lambda x: x if x.isdigit() else np.nan)

intervb1 = intervb1[['Event Code','latitude_intervention', 'longitude_intervention','abandon_reason','Postal Code']].rename(columns={'latitude_intervention':'latitude', 
                                                                                                           'longitude_intervention':'longitude',
                                                                                                           'abandon_reason':'Abandon_Reason'})
intervb2 = intervb2[['Event Code','Latitude intervention','Longitude intervention','Abandon reason FR','Postal Code']].rename(columns={'Latitude intervention':'latitude', 
                                                                                                           'Longitude intervention':'longitude',
                                                                                                           'Abandon reason FR':'Abandon_Reason'})
interventions = pd.concat([intervb1,intervb2], ignore_index=True).reset_index(drop=True)
interventions = interventions.loc[(~interventions['Abandon_Reason'].isin(['Error','Erreur']) | interventions['Event Code'].isin(['P039','P011','P003','P000'])),:]
interventions = interventions.dropna(subset=['longitude','latitude','Postal Code'])
interventions[['longitude','latitude']] = interventions[['longitude','latitude']].astype(int).astype(str)
interventions['Latitude'] = interventions['latitude'].apply(lambda x: x[:2] + '.' + x[2:])
interventions['Longitude'] = interventions['longitude'].apply(lambda x: x[:1] + '.' + x[1:])
interventions['Dead'] = np.where(interventions['Abandon_Reason'].isin(['DCD','Overleden']),'Yes','No')
interventions['Postal Code'] = interventions['Postal Code'].astype(int).astype(str)
interventions.drop(columns=['longitude','latitude'],inplace=True)
print(interventions.head())
print(interventions.tail())

#AEDs Cleaning
aed = aed[['Latitude','Longitude','Region','id']].dropna()
aed = aed[aed['Region']=='Brussels']
print(aed.head())
print(aed.tail())

#Ambulance cleaning
ambulances = ambulances[['latitude','longitude','departure_location_number','region']].rename(columns={'latitude':'Latitude','longitude':'Longitude','departure_location_number':'id'}).dropna()
ambulances = ambulances[ambulances['region']=='Brussels Hoofdstedelijk Gewest']
print(ambulances.head())
print(ambulances.tail())

#Exporting to excel
dir = os.getcwd()
interventions.to_excel(os.path.join(dir,'interventions.xlsx'), index=False)
aed.to_excel(os.path.join(dir,'aed.xlsx'), index=False)
ambulances.to_excel(os.path.join(dir,'ambulances.xlsx'), index=False)
