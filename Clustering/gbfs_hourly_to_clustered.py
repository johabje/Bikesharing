#This script is used to concat the gbfs data from all stations in a clusters


import pandas as pd
import os

def main(clusters, config):
    for cluster in clusters:
        count = 0
        gbfs_cluster = None
        for station in cluster:

            gbfs_station= pd.read_csv(f"Data/gbfs_station_hour/No/station_{int(station)}.csv", index_col="datetime", parse_dates=True)
            #If output folder does not exist, create it
            
            try:
                gbfs_cluster["bike_availability"] = gbfs_cluster["bike_availability"] + gbfs_station["bike_availability"]
                count += 1
            
            except:
                gbfs_cluster = gbfs_station
                count += 1
        
        gbfs_cluster["bike_availability"] = gbfs_cluster["bike_availability"]/count
        gbfs_cluster.to_csv(f"Data/gbfs_station_hour/{config}/station_{clusters.index(cluster)+1}.csv")
        print(f"Cluster {clusters.index(cluster)+1} done")

    