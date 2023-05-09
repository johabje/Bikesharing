
# Testcase for 30 days of data
# 1. Read trip data for each cluster from tripdata_2022_08.csv
# 2. Add weather data to each record
# 3. Add weekday binary to each record
# 4. Add hour of day to each record
# 5. Add month to each record
# 6. Add year to each record

import pandas as pd
import datetime as dt
import os
import holidays

def getStationCounts(stations, tripData, startTime, endTime):
    """Returns a dictionary with the hourly checkoutcount for each station"""
    #for each station in the cluster
    counts = dict()
    for station in stations:
        #slice the dataframe such that it only contains the station
        tripDatastation = tripData[tripData["start_station_id"] == station]
        tripDatastationDayHour = tripDatastation.groupby(pd.Grouper(freq='60Min')).count()
        tripDatastationDayHour.drop(columns=["start_station_id"], inplace=True)

        #add rows to the end of the dataframe for the missing hours
        firstIndex = tripDatastationDayHour.index[0]
        firstIndex= dt.datetime(firstIndex.year, firstIndex.month, firstIndex.day, firstIndex.hour, 0, 0)
        lastIndex = tripDatastationDayHour.index[-1]
        lastIndex= dt.datetime(lastIndex.year, lastIndex.month, lastIndex.day, lastIndex.hour, 0, 0)

        #number of rows missing at the beginning
        missingRowsStart = (firstIndex- startTime).seconds / 3600

        #number of rows missing at the end
        missingRowsEnd = (endTime  -lastIndex ).seconds / 3600

        #add rows to the beginning of the dataframe for the missing hours where counbt = 0
        for i in range(int(missingRowsStart)):
            new_row = pd.Series({"count": 0},name=pd.to_datetime(startTime + dt.timedelta(hours=i),utc=True))
            row = pd.DataFrame([new_row], columns=["count"])
            tripDatastationDayHour =pd.concat([row, tripDatastationDayHour])
        #add rows to the end of the dataframe for the missing hours where count = 0
        for i in range(int(missingRowsEnd)):

            tripDatastationDayHour.loc[pd.to_datetime(endTime - dt.timedelta(hours=i), utc=True)] = {'count': 0}
        #add rows for the missing days
        #make index column datetimeindex
        tripDatastationDayHour.index = pd.to_datetime(tripDatastationDayHour.index)
        tripDatastationDayHour = tripDatastationDayHour.sort_index()
        counts[station] = tripDatastationDayHour

    return counts




#create a new dataframe with the sum of
def getClusterCounts(clusters, counts):
    """Returns a dictionary with the hourly checkoutcount for each cluster"""
    i=0
    for cluster in clusters:
        i+=1
        df = pd.DataFrame()
        for station in cluster:
            if df.size == 0:
                try:
                    df = counts[station]
                    #remove counts[station] from counts
                    counts.pop(station)
                except:
                    print(f"station {station} not in counts")
            else:
                try:
                    df = df.add(counts[station], fill_value=0)
                    #remove counts[station] from counts
                    
                    counts.pop(station)
                except:
                    print(f"station {station} not in counts")
                    print("did the werid thing")
        #if the dataframe is still empty, fill it with zeros
        if df.size == 0:
            df = pd.DataFrame(0, index=pd.date_range(start=startTime, end=endTime, freq="H"), columns=["count"])
            print(df)
            print("did Zeros fill")
            df.index = pd.to_datetime(df.index)
        counts[i] = [df, cluster]
    return counts


#add weather data to each record
def AddWeatherData(counts):
    """adds weather data to each record in counts"""
    weather = pd.read_excel('Data/table.xlsx', index_col= "Tid(norsk normaltid)")
    weather = weather.drop(columns=["Navn", "Stasjon"])

    #skydekke column is reported at irregular intervals with "-" as missing value. replace all "-" with the last reported value
    for i in range(len(weather)):
        if weather["Skydekke"][i] == "-":
            weather["Skydekke"][i] = weather["Skydekke"][i-1]

    #convert index to datetimeindex
    weather.index = pd.to_datetime(weather.index, utc=True)

    #concat with all the dataframes in count, and add weather data to each record in count
    for station in counts:
        try:
            counts[station][0] = pd.concat([weather, counts[station][0]], axis=1, join="inner")
        except:
            counts[station] = [pd.concat([weather, counts[station]], axis=1, join="inner"), [station]]
    return counts

def stationDistances(year, month, stations):
    """Finds all stations within 500 meters of each station, and returns a dict with all stations, and their closest stations"""
    from haversine import haversine
    stations_dist = dict()
    #dict with stations, containig all stations within 500 meters, shuld be sorted by distance
    for index, row in stations.iterrows():
        #print(row)
        lat = row["lat"]
        lon = row["lon"]
        id = row["station_id"]
        close_stations = []
        for index2, row2 in stations.iterrows():
            if id == row2["station_id"]: continue
            dist = haversine({lat, lon}, {row2["lat"], row2["lon"]})
            if dist < 0.5:
                close_stations.append([int(row2["station_id"]), dist])
        close_stations = sorted(close_stations, key=lambda x: x[1], reverse=False)
        stations_dist[id] = close_stations
    return stations_dist, stations["station_id"]



def main(tripdata, startTime, endTime):
    #find all unique stations in tripdata, as a list of integers
    stations = tripdata["start_station_id"].unique()
    print(stations)
    stations = [int(station) for station in stations]
    print(stations)
    counts = getStationCounts(stations, tripdata, startTime, endTime)
    counts = AddWeatherData(counts)
    for station in counts:
        df = counts[station][0]
        #add weekday binary to each record
        print(type(df.index))
        if type(df.index) == pd.core.indexes.base.Index:
            print(df)
            print(counts[station])
        df["weekday"] = df.index.dayofweek
        #add hour of day to each record
        df["hour"] = df.index.hour
        #add isHoliday binary to each record
        df["isHoliday"] = df.index.isin(holidays.Norway(years=startTime.year).keys())
        # add count_last_hour to each record
        df["count_last_hour"] = df["count"].shift(1)
        counts[station][0] = df
        # @todo find the closest station or cluster to each station/cluster and add the count from that station to each record
        # how do we define closest station or cluster to each station/cluster? mayby borders along a voronoi diagram? most close stations will be in the same cluster

        
        
    #save counts to file
    for station in counts:
        counts[station][0].to_csv(f'Data/Dataset_NoClusters/06/{station}_{startTime.year}_{startTime.month}.csv', index=True)
    return counts, stations


startTime = dt.datetime(2022, 6, 1, 0, 0, 0)
endTime = dt.datetime(2022, 6, 30, 23, 0, 0)


tripdata = pd.read_csv("Data/tripdata/2022/06.csv", parse_dates=True)
tripdata["started_at"] = pd.to_datetime(tripdata["started_at"])
tripdata["count"] = 1
tripdata.drop(columns=["ended_at", "start_station_name", "end_station_id", "end_station_name", "start_station_description","end_station_description","duration", "start_station_latitude" , "start_station_longitude",  "end_station_latitude",  "end_station_longitude" ], inplace=True)
tripdata.set_index('started_at', inplace=True)
counts, stations = main(tripdata, startTime, endTime)

