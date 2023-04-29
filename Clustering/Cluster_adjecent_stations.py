#this file will use the tripdata for a spesific month to find all adjecent areas to each area and add the availability features to the dataset

import pandas as pd

def getAllStations(month):
    tripdata = pd.read_csv(f"Data/tripdata/2022/{month}.csv", parse_dates=True)
    tripdata["started_at"] = pd.to_datetime(tripdata["started_at"])
    print(587 in tripdata['start_station_id'].values)
    tripdata["count"] = 1
    tripdata.drop(columns=["ended_at", "start_station_name", "end_station_id", "end_station_name", "start_station_description","end_station_description","duration", "started_at","end_station_latitude", "end_station_longitude" ], inplace=True)
    #find each unique start station and its latitude and longitude
    start_stations = tripdata.drop_duplicates('start_station_id', keep='first')
    
    return start_stations


def stationDistances(year, month):
    """Finds all stations within 500 meters of each station, and returns a dict with all stations, and their closest stations"""
    from haversine import haversine
    stations_dist = dict()
    #dict with stations, containig all stations within 500 meters, should be sorted by distance
    stations = getAllStations(month)
    print(stations.head(5))
    for index, row in stations.iterrows():
        #print(row)
        lat = row["start_station_latitude"]
        lon = row["start_station_longitude"]
        id = row["start_station_id"]
        close_stations = []
        for index2, row2 in stations.iterrows():
            if id == row2["start_station_id"]: continue
            dist = haversine({lat, lon}, {row2["start_station_latitude"], row2["start_station_longitude"]})
            if dist < 0.5:
                close_stations.append(int(row2["start_station_id"]))
        
        stations_dist[id] = close_stations
    return stations_dist, stations["start_station_id"]



clusters = [{2347.0, 589.0}, {392, 443}, {401, 423}, {491, 483, 495}, {432, 578, 518}, {441, 452}, {576, 577, 545, 609, 547, 599, 2328, 2330, 478}, {2332, 500, 2334}, {489, 739, 2308, 437}, {618, 619}, {410, 399}, {481, 1101, 414}, {549, 396, 557, 526, 1023}, {434, 502}, {625, 387, 430}, {400, 530, 469, 389, 476}, {627, 572, 559}, {523, 574}, {453, 405}, {480, 522, 381}, {624, 586}, {558, 449, 1755, 2329}, {505, 471}, {550, 462}, {556, 446}, {534, 479}, {617, 421}, {472, 407}, {508, 413, 590}, {435, 748}, {509, 573}, {2280, 623, 390, 615}, {542, 551}, {2339, 475}, {587, 588}, {514, 506}, {442, 597}, {584, 459}, {611, 787, 571}, {620, 622}, {493, 598, 455}, {458, 415}, {431, 406, 487}, {398, 439}, {403, 564}, {408, 377}, {388, 548}, {426, 450, 519}, {496, 580}, {521, 412}, {594, 612}, {626, 746}, {448, 527}, {427, 613}, {537, 2337}, {498, 2270}, {411, 742}]

def main(clusters, year, month, month_int):
    startions = getAllStations(month)
    #fin all adjecent stations to each station
    neighbours, stations = stationDistances(year, month)
    cluster_neighbours = dict()
    #Now that we know the adjecent stations, we can find the clos station for a cluster
    #A clusters neigbours are all the adjecent stations to each station in the cluster

    for cluster in clusters:
        cluster_neighbours[clusters.index(cluster)+1] = []
        neighbours[clusters.index(cluster)+1] = []
        print(cluster)
        for station in cluster:
            print(station)
            try:
                for station_n in neighbours[station]:
                #print(neighbours[station_n])
                    if station_n not in cluster:
                        cluster_neighbours[clusters.index(cluster)+1].append(station_n)
                        print(station_n)
                        neighbours[station_n].remove(station)
                        neighbours[station_n].append(clusters.index(cluster)+1) if clusters.index(cluster)+1 not in neighbours[station_n] else neighbours[station_n]
                        neighbours[clusters.index(cluster)].append(station_n)+1 if station_n not in neighbours[clusters.index(cluster)+1] else neighbours[clusters.index(cluster)+1]
            except:
                #This means the station_n has no trips in the month, and is therefore not in the dataset
                continue
    #remove all stations that are in a cluster from neighbours
    for cluster in clusters:
        for station in cluster:
            try:
                neighbours.pop(station)
            except:
                #again, som stations are not in the dataset
                continue
                
        #add clusters to neighbours
        neighbours[clusters.index(cluster)+1] = cluster_neighbours[clusters.index(cluster)+1]

    print(neighbours)
        #if station in a cluster 
    #for all stations, add the adjecent stations to the dataset from the gbfs data
    
    #for each station in neighbours, add the availability features to the dataset. open data at Data/Dataset_Clusters/2022/{month}/station.csv.
    #for each neigbour the station has, open the gbfs hourly data set, and add the availability features to the dataset
    #save the dataset to Data/Dataset_Clusters/with_avail/2022/{month}/station.csv
    for station in neighbours:
        data= pd.read_csv(f"Data/Dataset_Clusters/{month}_norm/{int(station)}_{year}_{month_int}.csv", parse_dates=True)
        data.index = pd.to_datetime(data['Unnamed: 0'], utc=True)

        for neighbour in neighbours[station]:
            data2 = pd.read_csv(f"Data/gbfs_station_hour/station_{neighbour}.csv", parse_dates=True)
            data2.index = pd.to_datetime(data2['datetime'], utc=True)
            data=pd.merge(data,data2, how='inner', left_index=True, right_index=True)

        data.drop(list(data.filter(regex = 'datetime')), axis = 1, inplace = True)
        print(data)
        print(data.columns)
        #add availability data from the station itself
        data2 = pd.read_csv(f"Data/gbfs_station_hour/station_{int(station)}.csv", parse_dates=True)
        data2.index = pd.to_datetime(data2['datetime'], utc=True)
        data2.rename(columns={"bike_availability": "avaiability"}, inplace=True)
        
        data=pd.merge(data,data2, how='inner', left_index=True, right_index=True)
        
        data.drop(list(data.filter(regex = 'datetime')), axis = 1, inplace = True)
        data.to_csv(f"Data/Dataset_Clusters/with_avail/{month}_norm/{int(station)}_{year}_{month_int}.csv", index=False)


main(clusters, "2022", "06", 6)

