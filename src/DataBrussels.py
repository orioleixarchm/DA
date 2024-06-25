#Loading Packages
import pandas as pd
import numpy as np
import gdown

#Loading Data
links = [
    "https://drive.google.com/file/d/1VYm1Bs3I3k8BgZGPC_D0k0JEhPJzBKqJ/edit?usp=drive_link",
    "https://drive.google.com/file/d/1p0SIbiNYHE454hc4PSWH6E5dYycY36_K/edit?usp=drive_link",
    "https://drive.google.com/file/d/1vCBExpQ9N7-X084u3R55A_UxB0qao1Hx/edit?usp=drive_link",
    "https://drive.google.com/file/d/1uO1av0mAJtgUEj0Rb_4nFm1GMSmyUMjM/edit?usp=drive_link"
]

#Downloading data
file_ids = [link.split('/d/')[1].split('/')[0] for link in links]
urls = [f'https://drive.google.com/uc?id={file_id}' for file_id in file_ids]
gdown.download(urls[0], 'intervb1.parquet.gzip', quiet=False)
gdown.download(urls[1], 'intervb2.parquet.gzip', quiet=False)
gdown.download(urls[2], 'ambulances.parquet.gzip', quiet=False)
gdown.download(urls[3], 'aed.xlsx', quiet=False)
intervb1 = pd.read_parquet(f'intervb1.parquet.gzip')
intervb2 = pd.read_parquet(f'intervb2.parquet.gzip')
ambulances = pd.read_parquet(f'ambulances.parquet.gzip')
aed = pd.read_excel(f'aed.xlsx', dtype={'id':'str'})

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
ambulances = ambulances[['latitude','longitude','departure_location_number']].rename(columns={'latitude':'Latitude','longitude':'Longitude','departure_location_number':'id'}).dropna()
print(ambulances.head())
print(ambulances.tail())

#Exporting to excel
outpath='C:/Users/oriol/OneDrive/UNI/MASTER/Modern Data Analytics/Project/data/' #New path needs to be specified
interventions.to_excel(f'{outpath}interventions.xlsx', index=False)
aed.to_excel(f'{outpath}aed.xlsx', index=False)
ambulances.to_excel(f'{outpath}ambulances.xlsx', index=False)