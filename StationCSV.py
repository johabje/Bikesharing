import pandas as pd
import json

def getStationIds():
    station_ids = set()
    for i in range(0,1031):
        df = pd.read_csv(f"cleanCSVgbfs/{i:012}.csv")
        ids = df["station_id"].unique()
        print("station {} is done".format(i))
        for id in ids:
            station_ids.add(id)
    return station_ids

def getStationIdsJson():
    station_ids = set()
    with open('station_information.json', 'r') as f:
        stations = json.load(f)
        for station in stations['data']["stations"]:
            station_ids.add(int(station["station_id"]))
    return station_ids

from_json = getStationIdsJson()
from_gbfs = getStationIds()

print(from_gbfs)

if (from_json == from_gbfs):
    print("A-ok ser velidig bra ut")

else:
    print (from_gbfs.difference(from_json))
    print (from_json.difference(from_gbfs))

#we find that som stations are in gbfs but not in the current (08.11.2022) version of station_information.json have they been closed or wth is going on

def toStationCSV(stationList):
    count = 0
    lengt = len(stationList)
    for station in stationList:
        rows = pd.DataFrame()
        for i in range(0,1031):
            df = pd.read_csv(f"cleanCSVgbfs/{i:012}.csv")
            df = df.loc[df['station_id'] == station]
            rows = pd.concat([df, rows], ignore_index=True)
        rows.drop(columns=["Unnamed: 0"],inplace=True)
        rows.to_csv("gbfs_station_level/station_{}.csv".format(station))
        count += 1
        print("done with station {} out of {}".format(count, lengt))

toStationCSV(from_gbfs)