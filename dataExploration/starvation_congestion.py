import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Read the CSV file
def get_starv_con_percentage(station):
    df = pd.read_csv(f'Data/gbfs_station_level/{station}')

    df['last_reported'] = [datetime.fromtimestamp(x) for x in df["last_reported"]]

    #set last reported as index, ensure it is sorted accending
    df.set_index('last_reported', inplace=True)
    df.sort_index(inplace=True)
    #drop the columns we don't need
    df.drop(columns=["Unnamed: 0"], inplace=True)
    #create a new column, duration, with the time difference between the index time and the time after that
    df['duration'] = df.index.to_series().diff().dt.total_seconds()

    print(df.head(20))
    #summ all durations where the station was empty
    starvation_sum = df[df['num_bikes_available']==0]['duration'].sum()
    #summ all durations where the station was full
    congestion_sum = df[df['num_docks_available']==0]['duration'].sum()
    #calculate the total time
    total_time = df['duration'].sum()
    #calculate the percentage of time with no bikes available
    percentage_no_bikes = starvation_sum/total_time*100
    #calculate the percentage of time with no docks available
    percentage_no_docks = congestion_sum/total_time*100
    #print the results
    print(f"Percentage of time with no bikes available: {percentage_no_bikes:.2f}%")
    print(f"Percentage of time with no docks available: {percentage_no_docks:.2f}%")

    # Print the result
    print(f"Percentage of time with no bikes available: {percentage_no_bikes:.2f}%")
    return percentage_no_bikes, percentage_no_docks

import os
stations = os.listdir('Data/gbfs_station_level/')

station_starv_con = dict()
for station in stations:
    starv, con = get_starv_con_percentage(station)
    station_starv_con[station] = [starv, con]

#plot the results
x = [i[1][0] for i in station_starv_con.items()]

y = [i[1][1] for i in station_starv_con.items()]
plt.scatter(x, y)
plt.xlabel("Starvation (%)")
plt.ylabel("Congestion (%)")
plt.show()