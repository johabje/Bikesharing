
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

        print(tripDatastationDayHour.head(20))
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
                df = counts[station]
                #remove counts[station] from counts
                counts.pop(station)
            else:
                df = df.add(counts[station], fill_value=0)
                #remove counts[station] from counts
                counts.pop(station)
        print(df.head(20))
        counts[i] = [df, cluster]
    return counts


#add weather data to each record
def AddWeatherData(counts):
    """adds weather data to each record in counts"""
    weather = pd.read_excel('table.xlsx', index_col= "Tid(norsk normaltid)")
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



def main(tripdata, clusters, startTime, endTime):
    #find all unique stations in tripdata, as a list of integers
    stations = tripdata["start_station_id"].unique()
    stations = [int(station) for station in stations]
    
    counts = getStationCounts(stations, tripdata, startTime, endTime)
    counts = getClusterCounts(clusters, counts)
    counts = AddWeatherData(counts)
    
    #add weekday binary to each record

    #add hour of day to each record

    #add isHoliday binary to each record

    # add count_last_hour to each record

    
    #save counts to file
    for station in counts:
        counts[station][0].to_csv(f'Dataset_Clusters/{station}_{startTime.year}_{startTime.month}.csv', index=True)
    return counts, stations


startTime = dt.datetime(2022, 8, 1, 0, 0, 0)
endTime = dt.datetime(2022, 8, 31, 23, 0, 0)

clusters = [{2347.0, 589.0}, {392, 443}, {401, 423}, {491, 483, 495}, {432, 578, 518}, {441, 452}, {576, 577, 545, 609, 547, 599, 2328, 2330, 478}, {2332, 500, 2334}, {489, 739, 2308, 437}, {618, 619}, {410, 399}, {481, 1101, 414}, {549, 396, 557, 526, 1023}, {434, 502}, {625, 387, 430}, {400, 530, 469, 389, 476}, {627, 572, 559}, {523, 574}, {453, 405}, {480, 522, 381}, {624, 586}, {558, 449, 1755, 2329}, {505, 471}, {550, 462}, {556, 446}, {534, 479}, {617, 421}, {472, 407}, {508, 413, 590}, {435, 748}, {509, 573}, {2280, 623, 390, 615}, {542, 551}, {2339, 475}, {587, 588}, {514, 506}, {442, 597}, {584, 459}, {611, 787, 571}, {620, 622}, {493, 598, 455}, {458, 415}, {431, 406, 487}, {398, 439}, {403, 564}, {408, 377}, {388, 548}, {426, 450, 519}, {496, 580}, {521, 412}, {594, 612}, {626, 746}, {448, 527}, {427, 613}, {537, 2337}, {498, 2270}, {411, 742}]

tripdata = pd.read_csv("tripdata/2022/08.csv", parse_dates=True)
tripdata["started_at"] = pd.to_datetime(tripdata["started_at"])
tripdata["count"] = 1
tripdata.drop(columns=["ended_at", "start_station_name", "end_station_id", "end_station_name", "start_station_description","end_station_description","duration", "start_station_latitude" , "start_station_longitude",  "end_station_latitude",  "end_station_longitude" ], inplace=True)
tripdata.set_index('started_at', inplace=True)
counts, stations = main(tripdata, clusters, startTime, endTime)

