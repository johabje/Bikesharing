import os
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

def findAllStations(year, month):
    m = str(month)
    df = pd.read_csv(f"tripdata/{year}/{m.zfill(2)}.csv")
    df.drop_duplicates(subset=["start_station_id"],inplace=True)

    df.drop(["started_at","ended_at","duration","start_station_name",
    "start_station_description","end_station_id","end_station_name","end_station_description","end_station_latitude",
    "end_station_longitude"], axis = 1, inplace = True)
    df.rename(columns={"start_station_latitude": "lat", "start_station_longitude":"lon", "start_station_id": "station_id"}, inplace=True)
    print(df.head(20))
    return df
findAllStations(2022, 8)
def findAllStationsMod(year, month):
    m = str(month)
    df = pd.read_csv(f"tripdata/{year}/{m.zfill(2)}.csv")
    df.drop_duplicates(subset=["start_station_id"],inplace=True)

    df.drop(["started_at","ended_at","duration","start_station_name",
    "start_station_description","end_station_id",'start_station_longitude',
    'start_station_latitude',"end_station_name","end_station_description",
    "end_station_latitude","end_station_longitude"], axis = 1, inplace = True)
    
    #print(df.head(20))
    return df

#df_x=findAllStations(2022,6)
#stasjon_liste = list(df_x["start_station_id"])
#print(stasjon_liste)
#number of trips in a year from each station
def tripsFromStations():
    years = os.listdir("tripdata")
    years.remove('.DS_Store')
    yearly = dict()
    for year in years:
        months = os.listdir("tripdata/{}".format(year))
        lst = [Counter(pd.read_csv("tripdata/{}/{}".format(year, f))['start_station_id']) for f in os.listdir("tripdata/{}".format(year))]
        res = sum(lst, Counter())
        y_points = res.values()
        y_points = list(y_points)
        y_points.sort(reverse=True)
        x_points = list(range(0, len(y_points)))
        plt.plot(x_points, y_points, label=year)
        print(max(res))
    plt.xlabel("Stations")
    plt.ylabel("Number of trips")
    plt.show()
        #y_points = res[]
    print(years)


#tripsFromStations()
#number of trips to each station
def tripsToStations():
    years = os.listdir("tripdata")
    years.remove('.DS_Store')
    yearly = dict()
    for year in years:
        months = os.listdir("tripdata/{}".format(year))
        lst = [Counter(pd.read_csv("tripdata/{}/{}".format(year, f))['end_station_id']) for f in os.listdir("tripdata/{}".format(year))]
        print(lst)
        res = sum(lst, Counter())
        y_points = res.values()
        y_points = list(y_points)
        y_points.sort(reverse=True)
        print(y_points)
        x_points = list(range(0, len(y_points)))
        plt.plot(x_points, y_points, label=year)
    
    plt.xlabel("Stations")
    plt.ylabel("Number of trips")
    plt.legend()
    plt.show()

#tripsToStations()
#avrage trips per day, weekday vs weekend

def avrageMonthlyTotalDemand():
    path = "tripdata"
    years = os.listdir(path)
    years.remove(".DS_Store")
    years.remove("2019")
    month_counts = {"01": 0, "02": 0, "03": 0, "04": 0, "05": 0, "06": 0, "07": 0, "08": 0, "09": 0, "10": 0, "11": 0, "12": 0} 
    for year in years:
        months = os.listdir("{}/{}".format(path, year))
        for month in months:
            df = pd.read_csv('{}/{}/{}'.format(path, year, month))
            print("Number of rows ", len(df.index))
            month_counts["{}".format(month[:2])] += len(df.index)/3
    print(month_counts.keys())
    
    plt.bar(month_counts.keys(), month_counts.values())
    
    plt.show()

#avrageMonthlyTotalDemand()
#Example station demand thoroug a year, week, day
def stationDemand(station):
    df = pd.read_csv("tripdata/2019/06.csv")
    df['started_at'] = pd.to_datetime(df.started_at)
    station = df[df['start_station_id'] == station]
    mondays = station[station.started_at.dt.weekday == 0]
    sundays = station[station.started_at.dt.weekday == 6]
    thursdays = station[station.started_at.dt.weekday == 3]
    counts = mondays.started_at.dt.hour.value_counts().sort_index()
    plt.plot(counts,label= "monday")
    counts = sundays.started_at.dt.hour.value_counts().sort_index()
    plt.plot(counts, label="sunday")
    counts = thursdays.started_at.dt.hour.value_counts().sort_index()
    plt.plot(counts, label ="thursday")
    
    plt.xlabel("Hour")
    plt.ylabel("Number of check-outs")
    plt.legend()
    plt.show()

    counts = station.started_at.dt.date.value_counts().sort_index()
    plt.plot(counts)
    
    plt.show()

#stationDemand(413)


def availability(station_d, station_a):
    a_path = "gbfs/2021/8/21"
    df_a = pd.read_csv("{}/{}.csv".format(a_path,station_a))
    df_d = pd.read_csv("tripdata/2021/08.csv")
    df_d['started_at'] = pd.to_datetime(df_d.started_at)
    
    station_d_trips = df_d[df_d['start_station_id'] == station_d]
    station_d_trips = station_d_trips[station_d_trips["started_at"].dt.date == pd.to_datetime('8/21/2021').date()]
    print(station_d_trips)
    counts_d = station_d_trips.resample(rule='10T', on="started_at", convention='end').count()
    plt.plot(counts_d.index, counts_d.start_station_id, label="Trips")
    
    df_a["last_reported"] = pd.to_datetime(df_a.last_reported)
    res =df_a.resample(rule='10T', on="last_reported", convention='end').mean()
    plt.plot(df_a["last_reported"],df_a["num_bikes_available"], label = "Availability")
    print(df_a.head(40))
    plt.legend()
    plt.show()

valkyrien =390 
majorstuen = 471   
#availability(valkyrien, majorstuen)

def avrageTripDuration():
    path = "tripdata"
    years = os.listdir(path)
    years.remove(".DS_Store")
    years.remove("2019")
    month_avrage = {"01": 0, "02": 0, "03": 0, "04": 0, "05": 0, "06": 0, "07": 0, "08": 0, "09": 0, "10": 0, "11": 0, "12": 0} 
    year = "2021"
    months = os.listdir("{}/{}".format(path, year))
    for month in months:
        df = pd.read_csv('{}/{}/{}'.format(path, year, month))
        print("Number of rows ", len(df.index))
        month_avrage["{}".format(month[:2])] = df["duration"].mean()/60
    print(month_avrage.keys())
    
    plt.bar(month_avrage.keys(), month_avrage.values())
    plt.xlabel("Month")
    plt.ylabel("Duration (min)")
    plt.show()

#avrageTripDuration()

def varianceStationPair(from_id, to_id):
    path = "tripdata/2022"
    months = os.listdir(path)
    durations= []
    for month in months:
        df = pd.read_csv("{}/{}".format(path, month))
        df = df.loc[(df['start_station_id'] == from_id) & (df['end_station_id'] == to_id)]
        durations.extend(df["duration"].tolist())
        print("The mean duration between station {} and station {} is {}, while the variance is {} ".format(from_id, to_id, df["duration"].mean()/60, df["duration"].std()), "based on {} trips".format(len(df.index)))
    durations = map(lambda x: x/60, durations)
    df_t = pd.DataFrame(durations)
    mean = df_t[0].mean()
    std = df_t[0].std()
    data = df_t[0]
    plt.scatter(x=df_t.index, y=df_t[0])
    plt.hlines(y=mean - std, xmin=0, xmax=len(data), colors='r', label="1 std")
    plt.hlines(y=mean + std, xmin=0, xmax=len(data), colors='r')
    plt.hlines(y=mean - 2*std, xmin=0, xmax=len(data), colors='g', label="2 std")
    plt.hlines(y=mean + 2*std, xmin=0, xmax=len(data), colors='g')
    plt.xlabel("Trip")
    plt.ylabel("Duration (min)")
    plt.legend()
    plt.show()
#varianceStationPair(426, 623)

def tripsToStationsCDF():
    years = os.listdir("tripdata")
    years.remove('.DS_Store')
    yearly = dict()
    final = dict()
    length = 0
    for month in range(1,13):
        df = pd.read_csv(f'tripdata/2021/{str(month).zfill(2)}.csv')
        df2 = df.loc[df['end_station_id'] == 572]
        length += len(df2)
        lst = [Counter(df2['start_station_id'])]
        res = sum(lst, Counter())
        res = list(res.items())
        for key, value in res:
            final[key] = final.get(key, 0) + int(value)
    
    print(final.values())
    arr = np.array(list(final.values()))
    x = np.array(range(1,len(arr)+1))
    arr = -np.sort(-arr)
    print(arr)
    summ = np.sum(arr)
    print(summ)
    print(length)
    y = []
    for i in x:
        y.append(np.sum(arr[0:i])/summ)
    df = pd.DataFrame({'y': y, 'x': x} )
    print(df.loc[df['y'] > 0.99990000])
    print(df.loc[df['y'] > 0.990000])

    plt.subplot(1, 2, 1)
    plt.plot(x, y)
    plt.xlabel("Stations")
    plt.ylabel("Percentage of trips")
    plt.title("CDF ")
    plt.legend()
    years = os.listdir("tripdata")
    years.remove('.DS_Store')
    yearly = dict()
    final = dict()
    length = 0

    for month in range(1,13):
        df = pd.read_csv(f'tripdata/2021/{str(month).zfill(2)}.csv')
        df2 = df.loc[df['end_station_id'] == 423]
        length += len(df2)
        lst = [Counter(df2['start_station_id'])]
        res = sum(lst, Counter())
        res = list(res.items())
        for key, value in res:
            final[key] = final.get(key, 0) + int(value)
    
    print(final.values())
    arr = np.array(list(final.values()))
    x = np.array(range(1,len(arr)+1))
    arr = -np.sort(-arr)
    print(arr)
    summ = np.sum(arr)
    print(summ)
    print(length)
    y = []
    for i in x:
        y.append(np.sum(arr[0:i])/summ)
    df = pd.DataFrame({'y': y, 'x': x} )
    print(df.loc[df['y'] > 0.99990000])
    print(df.loc[df['y'] > 0.990000])
    plt.subplot(1, 2, 2)
    plt.plot(x, y)
    plt.xlabel("Stations")
    plt.ylabel("Percentage of trips")
    plt.title("CDF ")
    plt.legend()

    plt.show()

tripsToStationsCDF()

def varianceStationPairs(list):
    path = "tripdata/2022"
    months = os.listdir(path)
    
    for from_id in list:
        for to_id in list:
            durations= []
            variance = []
            for month in months:
                df = pd.read_csv("{}/{}".format(path, month))
                df = df.loc[(df['start_station_id'] == from_id) & (df['end_station_id'] == to_id)]
                durations.extend(df["duration"].tolist())
                #print("The mean duration between station {} and station {} is {}, while the variance is {} ".format(from_id, to_id, df["duration"].mean()/60, df["duration"].std()), "based on {} trips".format(len(df.index)))
                
            durations = map(lambda x: x/60, durations)
            df_t = pd.DataFrame(durations)
            if len(df_t) != 0:
                #print(df_t)
                mean = df_t[0].mean()
                std = df_t[0].std()
                variance.append(std)
                print(f'{std} from {from_id}, {to_id}, count: {len(df_t)}')
                data = df_t[0]
            """
            plt.scatter(x=df_t.index, y=df_t[0])
            plt.hlines(y=mean - std, xmin=0, xmax=len(data), colors='r', label="1 std")
            plt.hlines(y=mean + std, xmin=0, xmax=len(data), colors='r')
            plt.hlines(y=mean - 2*std, xmin=0, xmax=len(data), colors='g', label="2 std")
            plt.hlines(y=mean + 2*std, xmin=0, xmax=len(data), colors='g')
            plt.xlabel("Trip")
            plt.ylabel("Duration (min)")
            plt.legend()
            plt.show()
            """
    return variance


#var=varianceStationPairs(stasjon_liste)

#plt.plot(var)
#plt.show()