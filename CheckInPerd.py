import pandas as pd
#
def findAllStations(year, month):
    m = str(month)
    df = pd.read_csv(f"tripdata/{year}/{m.zfill(2)}.csv")
    df.drop_duplicates(subset=["start_station_id"],inplace=True)

    df.drop(["started_at","ended_at","duration","start_station_name","start_station_description","end_station_name","end_station_description","end_station_latitude","end_station_longitude","start_station_latitude","start_station_longitude" ], axis = 1, inplace = True)
    df.rename(columns = {'start_station_id':'station_id'}, inplace = True)
    print(df.head(260))
    return df

def get_probability_dict(year, month):
    df = pd.read_csv(f"tripdata/{year}/{month}.csv")
    df.drop(["started_at","ended_at","duration","start_station_name","start_station_description","end_station_name","end_station_description","end_station_latitude","end_station_longitude","start_station_latitude","start_station_longitude" ], axis = 1, inplace = True)
    all_stations = findAllStations(year, int(month))
    all_stations = list(all_stations["station_id"])
    print(all_stations)
    prob = dict() 
    for station in df.end_station_id.unique():
        prob[station] = {}
        for station_from in all_stations:
           
            total_count = len(df.loc[df["start_station_id"] == station_from])
            count = len(df.loc[(df["start_station_id"] == station_from) & (df["end_station_id"] == station)])
            if count == 0:
                prob[station][station_from] = 0
            else:
                prob[station][station_from] = count/total_count
    return prob
#get_probability_dict(2022, "08")

#predictions at all stations last hour, dict?
#yees, dict is good
def predictCheckIns(prob_station, Y_dict):
    count = 0
    for key in prob_station:
        count += Y_dict[key]*prob_station[key]
    return count
    

