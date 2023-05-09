#get a list of all stations
import pandas as pd
from dataPreperation.FinalDataset import findAllStations
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
                weigt = sim.statistic+math.log10(0.35/dist)
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

    return getWeigths(NewNodes, newSimVectors), NewNodes
        


        

def agglomerativeClustering(weigths, stations, simVectors, stationList):
    #return keys of the higest weigth in the weigths dict
    clusters = []
    #use the stations with the higest weigth as the first cluster
    maxWeigth = max(weigths, key=weigths.get)
    newNodes = stationList
    #loop while the higest weigth is larger than 1 and the number of clusters is larger than 175
    while max(weigths.values()) > 1 and len(newNodes) > 150:
        #if distance between the two stations is larger than 0.5, go to next biggest weigth
        #if both stations are clusters, merge the clusters
        if maxWeigth[0] in range(1,375) and maxWeigth[1] in range(1,375):
            print("merge")
            clusters[maxWeigth[0]-1] = clusters[maxWeigth[0]-1].union(clusters[maxWeigth[1]-1])
            clusters.pop(maxWeigth[1]-1)
        #if the "station" is actually a cluster, add the other station to the cluster
        elif maxWeigth[0] in range(1,375):
            print("add")
            clusters[maxWeigth[0]-1].add(maxWeigth[1])
        elif maxWeigth[1] in range(1,375):
            print("add")
            clusters[maxWeigth[1]-1].add(maxWeigth[0])
        #if one of the stations in the cluster is already in a cluster, add the connected station to the cluster
        
        #if both stations are not in a cluster, make a new cluster
        else:
            print("new")
            clusters.append(set(maxWeigth))
        #get the new set of weigths
        print(clusters)
        newweigths, newNodes = updateWeigths(clusters, stations, simVectors, stationList)
        maxWeigth = max(newweigths, key=newweigths.get)
        print(maxWeigth)
        weigths = newweigths
        
    return clusters





def main():
    k=3
    year = 2022
    month = "09"
    tripData = pd.read_csv(f"Data/tripdata/{year}/{month}.csv")
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