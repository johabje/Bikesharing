import pandas as pd
from FinalDataset import findAllStations
from scipy.stats.stats import pearsonr
from haversine import haversine
import math
import networkx as nx
import matplotlib.pyplot as plt
##from libpysal import weights, examples
from contextily import add_basemap
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
#import geopandas




def simVector(station, tripData):
    tripData = tripData[tripData["start_station_id"] == station]
    tripData["hour"] = tripData["started_at"].dt.hour
    tripData["count"] = 1
    #avrage count per hour vector
    avrCount = tripData.groupby("hour").sum()["count"]
    #make sure all hours are in the vector
    for i in range(24):
        if i not in avrCount.index:
            avrCount[i] = 0
    print (avrCount)
    return avrCount

def getWeigths(stations, simVectors):
    weigths =dict()
    for station1 in simVectors:
        #find lat and lon from lat/lon coulums in stations dataframe
        lat = stations.loc[stations["station_id"] == station1]["lat"].item()
        lon = stations.loc[stations["station_id"] == station1]["lon"].item()
        for station2 in simVectors:
            lat2 = stations.loc[stations["station_id"] == station2]["lat"].item()
            lon2 = stations.loc[stations["station_id"] == station2]["lon"].item()
            if station1 != station2:
                sim = pearsonr(simVectors[station1], simVectors[station2])
                dist = haversine((lat, lon), (lat2, lon2))
                weigths[(station1, station2)] = sim.statistic*math.log10(0.5/dist)
                #print (f'station {station1} and station {station2} have weigth: {weigths[(station1, station2)]}, and distance: {dist}')
    return weigths

def main():
    graph= nx.Graph()
    k=3
    year = 2022
    month = "09"
    tripData = pd.read_csv(f"tripdata/{year}/{month}.csv")
    tripData["started_at"] = pd.to_datetime(tripData["started_at"])
    tripData["ended_at"] = pd.to_datetime(tripData["ended_at"])
    stations = findAllStations(year, month)
    simVectors = dict()
    for index, row in stations.iterrows():
        station = row["station_id"]
        graph.add_node(station, pos=(row["lat"], row["lon"]))
        simVectors[station] = simVector(station, tripData)
    
    #pearson correlation and distance between all station pairs
    
    weigths = getWeigths(stations, simVectors)
    print (weigths)
    print(stations)
    #find K nearest neighbors for each station
    for station in stations["station_id"]:
        neighbors = dict()
        for station2 in stations["station_id"]:
            if station != station2:
                neighbors[station2] = weigths[(station, station2)]
        neighbors = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)
        for neighbor in neighbors[:k]:
            graph.add_edge(station, neighbor[0], weight= neighbor[1])

    #plot the graph using networkx

    options = {
    'node_color': 'black',
    'node_size': 50,
    'width': 3,
    }
    pos=nx.get_node_attributes(graph,'pos')
    ax= nx.draw(graph, pos, **options)
    add_basemap(ax)
    plt.show()


main()