import pandas as pd
import os
from datetime import datetime
from datetime import datetime, timedelta

# get a list of all the stations
def getStationList():
    stations = os.listdir("Data/Dataset_NoClusters/with_avail/09_2022")
    return stations

#get availability data for a station
def getAvailability(station):
    data = pd.read_csv(f'Data/gbfs_station_level/station_{station.partition(".")[0]}.csv', parse_dates=True)
    data.drop(columns=["Unnamed: 0", "station_id", "num_docks_available" ])
    data["last_reported"] = data["last_reported"].apply(lambda x: datetime.fromtimestamp(x))
    data.index = data["last_reported"]
    #drop rows so the index is unique
    data = data[~data.index.duplicated(keep='first')]
    data = data.resample('H').nearest()
    print(data)
    #data.index = pd.to_datetime(data['last_reported'], utc=True)
    return data

#for month, add the availability data to the station dataset
def addAvailability(station):
    months = os.listdir(f"Data/Dataset_NoClusters/with_avail/")
    avaialbility_data = getAvailability(station)
    for month in months:
        try:
            data_station = pd.read_csv(f"Data/Dataset_NoClusters/with_avail/{month}/{station}", parse_dates=True)
            #drop all colums named something with num_bikes_available
            data_station = data_station.drop(columns=[col for col in data_station.columns if 'num_bikes_available' in col])
            data_station.index = pd.to_datetime(data_station['Unnamed: 0'])
        except:
            print("No data for this station", f"Data/Dataset_NoClusters/with_avail/{month}/{station}")
            data_station = None
            continue
        data_station=data_station.tz_localize(None)
        #merge "num_bikes_available" and "num_docks_available", but no other colums from the availability data to the station dataset
        data_station=pd.merge(data_station,avaialbility_data[["num_bikes_available"]], how='inner', left_index=True, right_index=True)
        print(station)
        data_station.to_csv(f"Data/Dataset_NoClusters/with_avail/{month}/{station}", index=False)
    
        
    
stations = getStationList()
for station in stations:
    addAvailability(station)



