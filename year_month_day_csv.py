import pandas as pd
import json
import os

def getStationIds():
    station_ids = set()
    for i in range(0,1031):
        df = pd.read_csv(f"cleanCSVgbfs/{i:012}.csv")
        ids = df["station_id"].unique()
        print("station {} is done".format(i))
        for id in ids:
            station_ids.add(id)
    return station_ids

def datetimeFromUnix(stationList):
    import datetime as dt
    from pathlib import Path

    for station in stationList:
        df = pd.read_csv('gbfs_station_level/station_{}.csv'.format(station)).drop(columns=["Unnamed: 0"])
        df.sort_values(by=['last_reported'], inplace=True)
        df['last_reported'] = df['last_reported'].apply(lambda x: dt.datetime.fromtimestamp(x))
        print(df.head(20))
        print(df[-3:])
        for (last_reported), group in df.groupby(df["last_reported"].apply(lambda x: x.date())):
            print(group)
            
            date =  group["last_reported"].iloc[0]
            print(type(date))
            output_dir = Path('gbfs/{}/{}/{}'.format(date.year, date.month, date.day))
            output_dir.mkdir(parents=True, exist_ok=True)
            group.to_csv("{}/{}.csv".format(output_dir, station), index = False)

stationList= getStationIds()
datetimeFromUnix(stationList)

valkyrien =459 
majorstuen = 413


    