import pandas as pd
import os
from dateutil import rrule
from datetime import datetime
from datetime import datetime, timedelta

stations =os.listdir("Data/gbfs_station_level")

print(stations)

for station in stations:
    df = pd.read_csv("Data/gbfs_station_level/"+station)
    #find start and end date
    #convert last_reported to datetime
    
    #set last_reported as index
    start_stamp = df["last_reported"].min()
    end_stamp = df["last_reported"].max()
    start = datetime.fromtimestamp(start_stamp)
    end = datetime.fromtimestamp(end_stamp)
    end = end.replace(minute=0, second=0, microsecond=0)
    start = start.replace(minute=0, second=0, microsecond=0)
    
    num_bikes_available = df.query("last_reported==@start_stamp")["num_bikes_available"]
    num_bikes_available = int(num_bikes_available.iloc[0])
    num_docks_available = df.query("last_reported==@start_stamp")["num_docks_available"]
    num_docks_available = int(num_docks_available.iloc[0])
    df["last_reported"] = [datetime.fromtimestamp(x) for x in df["last_reported"]]
    print(start)
    print(end)
    print("new station")
    new_dataframe = pd.DataFrame(columns=["datetime", "bike_availability", "dock_availability"])
    #for each hour in the period, find percentage of time the station is empty (0 bikes available)
    
    
    for dt in rrule.rrule(rrule.HOURLY, dtstart=start, until=end):
        #get all rows for the hour
        print(dt)
        mask = (df['last_reported'] > dt) & (df['last_reported'] <= dt+timedelta(hours=1))
        hour = df.loc[mask]
        hour.sort_values(by='last_reported', ascending = True, inplace = True)
        last_time = dt
        available_bikes = 0
        available_locks = 0
        for row in hour.iterrows():
            duration = row[1]["last_reported"] - last_time
            duration_in_h = duration.total_seconds()/3600
            if num_docks_available != 0:
                available_bikes += duration_in_h
            if row[1]["num_docks_available"] != 0:
                available_locks += duration_in_h

            last_time = row[1]["last_reported"]
            num_bikes_available = row[1]["num_bikes_available"]
            num_docks_available = row[1]["num_docks_available"]
        new_dataframe= new_dataframe.append({"datetime": dt, "bike_availability": available_bikes, "dock_availability": available_locks}, ignore_index=True)
    print(new_dataframe)
    #store the new dataframe
    new_dataframe.to_csv("Data/gbfs_station_hour/"+station, index=False)
    #for each hour in the period, find percentage of time the station is full (0 docks available)

