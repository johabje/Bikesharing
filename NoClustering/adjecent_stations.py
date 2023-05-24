#this file will use the tripdata for a spesific month to find all adjecent areas to each area and add the availability features to the dataset
import pandas as pd
from haversine import haversine
import os
def getAllStations(month):
    tripdata = pd.read_csv(f"Data/tripdata/2022/{month}.csv", parse_dates=True)
    tripdata["started_at"] = pd.to_datetime(tripdata["started_at"])
    tripdata["count"] = 1
    tripdata.drop(columns=["ended_at", "start_station_name", "end_station_id", "end_station_name", "start_station_description","end_station_description","duration", "started_at","end_station_latitude", "end_station_longitude" ], inplace=True)
    #find each unique start station and its latitude and longitude
    start_stations = tripdata.drop_duplicates('start_station_id', keep='first')
    
    return start_stations

def getNearestStations(stations, target_station, max_distance):
    nearest_stations = []
    for index, row in stations.iterrows():
        if row["start_station_id"] != target_station:
            dist = haversine((row["start_station_latitude"], row["start_station_longitude"]), (stations.loc[stations["start_station_id"] == target_station, ["start_station_latitude", "start_station_longitude"]].values[0][0], stations.loc[stations["start_station_id"] == target_station, ["start_station_latitude", "start_station_longitude"]].values[0][1]))
            if dist < max_distance:
                nearest_stations.append(row["start_station_id"])
    return nearest_stations

def createStationDatasets(year, month, max_distance):
    stations = getAllStations(month)
    for index, row in stations.iterrows():
        target_station = row["start_station_id"]
        print(f"Processing station {target_station}...")
        nearest_stations = getNearestStations(stations, target_station, max_distance)
        station_data = pd.read_csv(f"Data/Dataset_NoClusters/{month}/{int(target_station)}_{year}_{int(month)}.csv", parse_dates=True)
        station_data.index = pd.to_datetime(station_data['Unnamed: 0'], utc=True)
        for nearest_station in nearest_stations:
            
            data2 = pd.read_csv(f"Data/gbfs_station_hour/No/station_{int(nearest_station)}.csv", parse_dates=True)
            data2.index = pd.to_datetime(data2['datetime'], utc=True)
            data2.rename(columns={"bike_availability": f"bike_availability_{nearest_station}", "dock_availability": f"dock_availability_{nearest_station}"}, inplace=True)
            #print(data2)
            station_data=pd.merge(station_data,data2, how='inner', left_index=True, right_index=True)
            
        station_data.drop(list(station_data.filter(regex = 'datetime')), axis = 1, inplace = True)
        print(station_data)
        print(station_data.columns)
        if not os.path.exists(f"Data/Dataset_NoClusters/with_avail/{month}"):
            os.makedirs(f"Data/Dataset_NoClusters/with_avail/{month}")

        station_data.to_csv(f"Data/Dataset_NoClusters/with_avail/{month}/{target_station}.csv", index=False)
        
createStationDatasets(2022, "09", 0.2)