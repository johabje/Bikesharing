#get a list of all stations
from FinalDataset import findAllStations
import pandas as pd
from FinalDataset import findAllStations
from scipy.stats import pearsonr
from haversine import haversine
import math
import networkx as nx
import matplotlib.pyplot as plt
##from libpysal import weights, examples
from contextily import add_basemap
import networkx as nx
import numpy as np
import mplleaflet

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
    #print (avrCount)
    return avrCount
#Kan gjøres veldig mye mer effektivt, vi bør ikke trenge å gå gjennom alle stasjonene for hver stasjon. spesielt ikke når vi opdaterer for clusters. 
def getWeigths(stations, simVectors):
    weigths =dict()
    for station1 in simVectors:
        weigthlist = []
        #find lat and lon from lat/lon coulums in stations dataframe
        lat = stations.loc[stations["station_id"] == station1]["lat"].item()
        lon = stations.loc[stations["station_id"] == station1]["lon"].item()
        for station2 in simVectors:
            lat2 = stations.loc[stations["station_id"] == station2]["lat"].item()
            lon2 = stations.loc[stations["station_id"] == station2]["lon"].item()
            if station1 != station2:
                sim = pearsonr(simVectors[station1], simVectors[station2])
                dist = haversine((lat, lon), (lat2, lon2))
                weigt = sim.statistic+math.log10(0.5/dist)
                #if weigth is larger than the smallest weigth in the list, add it to the list
                if len(weigthlist) < 3:
                    weigthlist.append((station2, weigt))
                else:
                    weigthlist = sorted(weigthlist, key=lambda x: x[1], reverse=True)
                    if weigt > weigthlist[2][1]:
                        weigthlist[2] = (station2, weigt)
                #print (f'station {station1} and station {station2} have weigth: {weigths[(station1, station2)]}, and distance: {dist}')
        #add the three closest stations to the weigths dict
        weigths[station1, weigthlist[0][0]] = weigthlist[0][1]
        weigths[station1, weigthlist[1][0]] = weigthlist[1][1]
        weigths[station1, weigthlist[2][0]] = weigthlist[2][1]
    return weigths

def location(cluster, stations):
    lat = 0
    lon = 0
    for station in cluster:
        lat += stations.loc[stations["station_id"] == station]["lat"].item()
        lon += stations.loc[stations["station_id"] == station]["lon"].item()
    lat = lat/len(cluster)
    lon = lon/len(cluster)
    return lat, lon

def simVectorClusters(cluster ,simVectors):
    simVector = np.zeros(24)
    for station in cluster:
        simVector += simVectors[station]
        simVector = simVector/len(cluster)
    return simVector


def updateWeigths(clusters, stations, simVectors, stationList):
    weigths = dict()
    NewNodes = pd.DataFrame()
    stations_in_clusters = []
    n=0
    newSimVectors = dict()
    for cluster in clusters:
        n+=1
        lat, lon = location(cluster, stations)
        simVector = simVectorClusters(cluster, simVectors)
    
        for station in cluster:
            stations_in_clusters.append(station)
        NewNodes = NewNodes.append(pd.DataFrame({"station_id": n, "lat": lat, "lon": lon}, index=[n]))
        newSimVectors[n] = simVector
    #append all stations not in a cluster:
    for station in stationList:
        if float(station) not in stations_in_clusters:
            NewNodes = NewNodes.append(pd.DataFrame({"station_id": station, "lat": stations.loc[stations["station_id"] == station]["lat"].item(), "lon": stations.loc[stations["station_id"] == station]["lon"].item()}, index=[station]))
            newSimVectors[station] = simVectors[station]
    print(NewNodes)

    return getWeigths(NewNodes, newSimVectors)
        


        

def agglomerativeClustering(weigths, stations, simVectors, stationList):
    #return keys of the higest weigth in the weigths dict
    clusters = []
    #use the stations with the higest weigth as the first cluster
    maxWeigth = max(weigths, key=weigths.get)
    while max(weigths.values()) > 0.5:
        #if both stations are already in a cluster, merge the clusters so they are contained in one cluster
        found = False
        for cluster1 in clusters:
            for cluster2 in clusters:
                if cluster1 != cluster2 and maxWeigth[0] in cluster1 and maxWeigth[1] in cluster2:
                    print("merge")
                    print("before: ", clusters)
                    cluster = cluster1.union(cluster2)
                    clusters.append(cluster)
                    print(clusters)
                    clusters.remove(cluster2)
                    clusters.remove(cluster1)
                    print(clusters)
                    found = True
                    break
            if found:
                break
        #if one of the stations in the cluster is already in a cluster, add the connected station to the cluster
        if not found:
            for cluster in clusters:
                print(maxWeigth[0], maxWeigth[1])
                print(cluster)
                if maxWeigth[0] in cluster or maxWeigth[1] in cluster:
                    print("add")
                    cluster.add(maxWeigth[0])
                    cluster.add(maxWeigth[1])
                    break
            #if both stations are not in a cluster, make a new cluster
            else:
                print("new")
                clusters.append(set(maxWeigth))
        #get the new set of weigths
        newweigths = updateWeigths(clusters, stations, simVectors, stationList)
        maxWeigth = max(newweigths, key=newweigths.get)
        print(maxWeigth)
        print(clusters)
    return clusters





def main():
    k=3
    year = 2022
    month = "09"
    tripData = pd.read_csv(f"tripdata/{year}/{month}.csv")
    tripData["started_at"] = pd.to_datetime(tripData["started_at"])
    tripData["ended_at"] = pd.to_datetime(tripData["ended_at"])
    stations = findAllStations(year, month)
    stationList = stations["station_id"].tolist()
    simVectors = dict()
    for index, row in stations.iterrows():
        station = row["station_id"]
        simVectors[station] = simVector(station, tripData)

    weigths = getWeigths(stations, simVectors)

    clusters = agglomerativeClustering(weigths, stations, simVectors, stationList)
    print(clusters)
    #nx.draw(graph, with_labels=Tr

main()