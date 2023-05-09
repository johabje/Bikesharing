
# 1. List all stations, with lat/long

# 2. For each station, find all stations within 500 meters

# 3. from trips, add cekh in count
# 4. from availability, add avalability at other stations
# 5. from weather data, add weatherdata

# What time inkrement should we use? variable for now, default one hour

#first date in availability is 2020/03/09

import pandas as pd
import os
import warnings
import holidays
from datetime import date
import datetime
warnings.simplefilter(action='ignore', category=FutureWarning)


def findAllStations(year, month):
    """Finds all stations in a given month, and returns a dataframe with all stations, and their lat/long"""
    m = str(month)
    df = pd.read_csv(f"Data/tripdata/{year}/{m.zfill(2)}.csv")
    df.drop_duplicates(subset=["start_station_id"],inplace=True)

    df.drop(["started_at","ended_at","duration","start_station_name","start_station_description","end_station_id","end_station_name","end_station_description","end_station_latitude","end_station_longitude"], axis = 1, inplace = True)
    df.rename(columns = {'start_station_id':'station_id', 'start_station_latitude':'lat', "start_station_longitude":"lon"}, inplace = True)
    #print(df.head(20))
    return df


def stationDistances(year, month):
    """Finds all stations within 500 meters of each station, and returns a dict with all stations, and their closest stations"""
    from haversine import haversine
    stations_dist = dict()
    #dict with stations, containig all stations within 500 meters, shuld be sorted by distance
    stations = findAllStations(year, month)
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
#stationDistances(2020, 5)

def findAvailability(year,month, day, hour, min, station_id, df):
    """finds the number of available bikes at a given station at a given time, returns 0 if no data is available"""
    dt = pd.to_datetime(f"{year}-{month}-{day} {hour}:{min}:00.000")
    df.index = pd.to_datetime(df.index)
    s = df.loc[df.index.unique()[df.index.unique().get_loc(dt, method='nearest')]]
    try:
        return s.iloc[0]["num_bikes_available"]
    except:
        return s["num_bikes_available"]

def getweather(year,month, day, hour, df):
    """finds the weather at a given time, returns 0 if no data is available"""
    dt = pd.to_datetime(f"{year}-{month}-{day} {hour}:00:00.000")
    df.index = pd.to_datetime(df.index)
    s = df.loc[dt]
    return s["Nedbør (1 t)"], s["Lufttemperatur"], s["Middelvind"]

#print( f'return from func {findAvailability(2020, 6, 1, 6, 496)}')
#getweather(2020, 4, 9, 11)


def getTripCount(year,month, day, hour, df):
    """finds the number of trips at a given time imterval, returns 0 if no data is available"""
    dt = pd.to_datetime(f"{year}-{month}-{day} {hour}:00:00.000")
    count = df.resample("H").agg({'count':'sum'})
    try:
        return count.loc[dt, "count"]
    except:
        return 0


def main():
    df_w = pd.read_excel('table.xlsx', index_col= "Tid(norsk normaltid)")
    no_holidays = holidays.NO()
    for year in [2021]:
        for month in [10]:
            stations_dist, stations = stationDistances(year, month)
            
            for station in stations:

                m = str(month)
                month_data = []
                try:
                    tripdata= pd.read_csv(f'tripdata/{year}/{m.zfill(2)}.csv', index_col="started_at")
                    tripdata['start_station_id'] = tripdata['start_station_id'].astype('int')
                    tripdata = tripdata.loc[tripdata['start_station_id'] == station]
                    tripdata.index = pd.to_datetime(tripdata.index)
                    tripdata['count'] = 1
                except:
                    continue
                
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    days =32
                elif month in [4, 6, 9, 11]:
                    days = 31
                else:
                    days = 29
                for day in range(1, days):
                    avails = []
                    for closestation in stations_dist[station]:
                        try:
                            avails.append(pd.read_csv(f'gbfs/{year}/{month}/{day}/{closestation[0]}.csv', index_col="last_reported"))
                        except:
                            print("no availabiliy")
                    if len(avails) == 0: continue
                    for hour in range(0, 24):
                        for min in range(0,61,15):
                        #available bikes per station
                            row = dict()
                            if stations_dist[station] == []:
                                break
                            count=0
                            
                            for closestation in stations_dist[station]:
                                print(closestation)
                                try:
                                    row[f'availability {count}'] = findAvailability(year, month, day, hour, min, closestation[0], avails[count])
                                except:
                                    row[f'availability {count}'] = None
                                count+=1
                            #weather
                            try:
                                nedbør, temp, vind = getweather(year, month, day, hour, df_w)
                                row["precititation"] = nedbør
                                row["temp"] = temp 
                                row["Wind"] = vind
                                row["hour"] = hour
                                
                            except:
                                print("no weather data")
                                continue
                            row["count"] = getTripCount(year, month, day, hour, tripdata)
                            #get current availability
                            last_hour= hour-1
                            if last_hour == -1:
                                row["count_last_hour"] = None
                            else: row["count_last_hour"] = getTripCount(year, month, day, last_hour, tripdata)
                            
                            hour = hour+1
                            if hour == 24: hour=0
                            row["dateTime"] = pd.to_datetime(f"{year}-{month}-{day} {hour}:00:00.000")
                            dato = date(year, month, day)
                            row["isHoliday"] = dato in no_holidays
                            row["weekday"] = dato.weekday()
                            #print(f"the row is: {row}")
                            month_data.append(row)
                month_data = pd.DataFrame.from_dict(month_data, orient='columns')
                
                if month_data.size == 0: continue

                outdir = f'finalData/{year}/{month}'
                if not os.path.exists(outdir):
                    os.makedirs(outdir, exist_ok=True)
                month_data.to_csv(f'finalData/{year}/{month}/{station}.csv',index=False)

def addMonth():
    """Adds a month column to the csv files"""
    for year in os.listdir("finalData"):
        for month in os.listdir(f'finalData/{year}'):
            for station in os.listdir(f'finalData/{year}/{month}'):
                path = f'finalData/{year}/{month}/{station}'
                print(path)
                df = pd.read_csv(path)
                df["month"] = int(month)
                print(df.head(20))
                print(month)
                df.to_csv(path, index=False)



def findAllStations_in(year, month):
    """Finds all stations in a given month"""
    m = str(month)
    df = pd.read_csv(f"Data/tripdata/{year}/{m.zfill(2)}.csv")
    df.drop_duplicates(subset=["start_station_id"],inplace=True)

    df.drop(["started_at","ended_at","duration","start_station_name","start_station_description",
            "start_station_longitude","start_station_latitude","end_station_name","start_station_id",
            "end_station_description","end_station_latitude","end_station_longitude"], axis = 1, inplace = True)

    #print(df.head(20))
    return df

import json
def checkInCounts():
    """creates a Json dictionary with the check in counts for each station each hour in the prediction period"""
    f4 = open('results3/CI_pred.json')
    stations = list(json.load(f4).keys())


    for year in [2022]:
        CI_true = dict()
        tripdata= pd.read_csv(f'tripdata/{year}/10.csv', index_col="started_at")
        tripdata["end_station_id"]= tripdata["end_station_id"].astype('int')
        tripdata.drop(inplace = True, columns=['ended_at', 'duration', 'start_station_id', 'start_station_name', 'start_station_description', 'start_station_latitude', 'start_station_longitude', 'end_station_name', 'end_station_description', 'end_station_latitude', 'end_station_longitude'])
        for station in stations:
                CI_true[int(station)]= []
        print(CI_true)
        month = 10
        for station in stations:
            print(station)
            #print(row["end_station_id"])
            m = str(month)
            month_data = []
            
            tripdata_station = tripdata.loc[tripdata['end_station_id'] == int(station)]
            tripdata_station.index = pd.to_datetime(tripdata_station.index)
            tripdata_station['count'] = 1
            print(tripdata_station)
            #print(tripdata.head(50))
            
            if month in [1, 3, 5, 7, 8, 10, 12]:
                days =32
            elif month in [4, 6, 9, 11]:
                days = 31
            else:
                days = 29
            for day in range(1, days):
                for hour in range(0, 24):
                    #print(tripdata.head(40))
                    count = getTripCount(year, month, day, hour, tripdata_station)
                    #print(count)
                    CI_true[int(station)].append(int(count))
            
            res = list(CI_true[int(station)][-168:])
            print(res)
            CI_true[int(station)] = res
    
    with open('results3/CI_true.json', 'w') as fp:
        json.dump(CI_true, fp)

#checkInCounts()
def stationDistancesMod(year, month):
    """Finds all stations within 500 meters of each station, returns only station ids sorted by distance"""
    from haversine import haversine
    stations_dist = dict()
    #dict with stations, containig all stations within 500 meters, should be sorted by distance
    stations = findAllStations(year, month)
    for index, row in stations.iterrows():
        #print(row)
        lat = row["lat"]
        lon = row["lon"]
        id = row["station_id"]
        if int(id) == 606:
            print ("606 found!!!!!!")
        close_stations = []
        for index2, row2 in stations.iterrows():
            if id == row2["station_id"]: continue
            dist = haversine({lat, lon}, {row2["lat"], row2["lon"]})
            if dist < 0.5:
                close_stations.append([int(row2["station_id"]), dist])
        close_stations = sorted(close_stations, key=lambda x: x[1], reverse=False)
        if int(id) == 606:
            print(close_stations)
        stations_dist[id] = [i[0] for i in close_stations]
        #print(stations_dist)
    return stations_dist

import numpy as np
def Availabilityasbinary():
    """Makes the availability columns binary"""
    for year in os.listdir("finalData"):
        for month in os.listdir(f'finalData/{year}'):
            for station in os.listdir(f'finalData/{year}/{month}'):

                path = f'finalData/{year}/{month}/{station}'
                print(path)
                df = pd.read_csv(path)
                filter_col = [col for col in df if col.startswith('availability')]
                for col in filter_col:
                    df[col] = np.where(df[col]>1, 1, df[col])
                print(df.head(20))
                print(month)
                # open df for related stations
                
                # get count for each dt
                # get mean
                os.makedirs(f'finalData2/{year}/{month}', exist_ok=True)
                df.to_csv(f'finalData2/{year}/{month}/{station}', index=False)

#Availabilityasbinary()

def addMeanCountLastHour(station, close_stations):
    """Adds a column with the mean count of the last hour for each station"""
    
    for year in os.listdir("finalData2"):
        for month in os.listdir(f'finalData2/{year}'):
            if len(close_stations[station])==0:
                try:
                    df = pd.read_csv(f'finalData2/{year}/{month}/{station}.csv', index_col="dateTime")
                    df.index = pd.to_datetime(df.index)
                    df["Mean_close_count_last_hour"] = 0
                except:
                    x=1
                    print("no data found")
                continue
            try:
                df = pd.read_csv(f'finalData2/{year}/{month}/{station}.csv', index_col="dateTime")
                df.index = pd.to_datetime(df.index)
                df["Mean_close_count_last_hour"] = 0
            except:
                print(f"no data for station {station}, year {year}, month {month}")
                continue
            #print(df)
            close_dfs = []
            for stat in close_stations[station]:
                try:
                    temp = pd.read_csv(f'finalData/{year}/{month}/{stat}.csv', index_col="dateTime")
                    temp.index = pd.to_datetime(temp.index)
                    close_dfs.append(temp)
                    #print(temp.head(20))
                except:
                    print("no data avialable for neigbour station ", stat)
            if month in [1, 3, 5, 7, 8, 10, 12]:
                days =32
            elif month in [4, 6, 9, 11]:
                days = 31
            else:
                days = 29
            for day in range(1, days):
                for hour in range(0,23):
                    dt = pd.to_datetime(f"{year}-{month}-{day} {hour}:00:00.000")
                    counts = []
                    fails = 0
                    for df_t in close_dfs:
                        try:
                            counts.append(int(df_t.loc[[dt]]["count"].values))
                        except:
                            counts.append(0)
                            fails +=1
                    try:

                        f_count = sum(counts)/len(counts)
                    except:
                        f_count=0
                    dt_1 = dt + pd.DateOffset(hours = 1)
                    #print(dt_1)
                    try:
                        x =df.at[dt_1, "Mean_close_count_last_hour"]
                    except:
                        continue
                    df.loc[dt_1, "Mean_close_count_last_hour"] = f_count
                    #print(df.at[dt_1, "Mean_close_count_last_hour"])
            
            #print(df)
            df.to_csv(f'finalData2/{year}/{month}/{station}.csv')
            print(fails)


#close_stations=stationDistancesMod(2022, 8)



#print(f'now doing station{602}')
#addMeanCountLastHour(553, close_stations)

def finalData3to3():
    """Finds the sum of binary availabilities replaces them with their sum"""
    for year in os.listdir("finalData2"):
        for month in os.listdir(f"finalData2/{year}"):
            for station in os.listdir(f"finalData2/{year}/{month}"):

                df = pd.read_csv(f"finalData2/{year}/{month}/{station}")
                col_list= list(df)
                col_list.remove('nedør')
                col_list.remove('temp')
                col_list.remove('vind')
                col_list.remove('hour')
                col_list.remove('count')
                col_list.remove('count_last_hour')
                col_list.remove('isHoliday')
                col_list.remove('weekday')
                try:
                    col_list.remove('month')
                except:
                    df['month']= int(month)
                try:
                    col_list.remove('Mean_close_count_last_hour')
                except:
                    df["Mean_close_count_last_hour"] = 0
                col_list.remove('dateTime')

                df['availability'] = df[col_list].sum(axis=1)

                print(df.info())
                df = df.loc[:, ['dateTime',"nedør",'temp','vind','hour','count','count_last_hour','isHoliday','weekday','month','availability', 'Mean_close_count_last_hour']]
                print(df.info())
                df.to_csv(f"finalData3/{year}/{month}/{station}",index=False)

#finalData3to3()