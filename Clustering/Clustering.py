import pandas as pd
from scipy.stats.stats import pearsonr
from scipy.spatial import Voronoi, voronoi_plot_2d
from haversine import haversine
import math
import networkx as nx
import matplotlib.pyplot as plt
##from libpysal import weights, examples
from contextily import add_basemap
import networkx as nx
import numpy as np
import distinctipy as dp
import mplleaflet
#import geopandas

def findAllStations(year, month):
    """Finds all stations in a given month, and returns a dataframe with all stations, and their lat/long"""
    m = str(month)
    df = pd.read_csv(f"Data/tripdata/{year}/{m.zfill(2)}.csv")
    df.drop_duplicates(subset=["start_station_id"],inplace=True)

    df.drop(["started_at","ended_at","duration","start_station_name","start_station_description","end_station_id","end_station_name","end_station_description","end_station_latitude","end_station_longitude"], axis = 1, inplace = True)
    df.rename(columns = {'start_station_id':'station_id', 'start_station_latitude':'lat', "start_station_longitude":"lon"}, inplace = True)
    #print(df.head(20))
    return df


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
                weigths[(station1, station2)] = sim.statistic+math.log10(0.25/dist)
                #print (f'station {station1} and station {station2} have weigth: {weigths[(station1, station2)]}, and distance: {dist}')
    return weigths

def getGE():
    graph= nx.Graph()
    k=3
    year = 2022
    month = "09"
    tripData = pd.read_csv(f"Data/tripdata/{year}/{month}.csv")
    tripData["started_at"] = pd.to_datetime(tripData["started_at"])
    tripData["ended_at"] = pd.to_datetime(tripData["ended_at"])
    stations = findAllStations(year, month)
    simVectors = dict()
    for index, row in stations.iterrows():
        station = row["station_id"]
        graph.add_node(station, pos=(row["lon"],row["lat"]))
        simVectors[station] = simVector(station, tripData)
    
    #pearson correlation and distance between all station pairs

    weigths = getWeigths(stations, simVectors)
    #find K nearest neighbors for each station
    for station in stations["station_id"]:
        neighbors = dict()
        for station2 in stations["station_id"]:
            if station != station2:
                neighbors[station2] = weigths[(station, station2)]
        #remove negative weigths
        for neighbor in neighbors:
            if neighbors[neighbor] < 0:
                neighbors[neighbor] = 0
        neighbors = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)
        #print(neighbors)
        for neighbor in neighbors[:k]:
            graph.add_edge(station, neighbor[0], weight= neighbor[1])
    
    return graph, simVectors, stations


def getClusters(graph, m):
    """get clusters from the graph, until there are m clusters. Returns the clusters and the new graph"""
    #sort edges by weight
    #remove edges from the graph, until there are m clusters
    while nx.number_connected_components(graph) < m:
        #find the largest cluster
        clusters = nx.algorithms.components.connected_components(graph)
        largestCluster = max(clusters, key=len)
        #find the edge with the largest weight in the largest cluster
        edges = sorted(graph.edges(data=True), key=lambda x: x[2]["weight"], reverse=False)
        for edge in edges:
            if edge[0] in largestCluster and edge[1] in largestCluster:
                graph.remove_edge(edge[0], edge[1])
                break
        #remove one edge from the largest cluster in the graph
    #return the clusters and the new graph
    return nx.algorithms.community.greedy_modularity_communities(graph, cutoff=m, best_n=m), graph

def getClusters2(graph, m):
    #reove edges from the graph, until there are m clusters
    while nx.number_connected_components(graph) < m:
        #find the egde with the largest weight
        edges = sorted(graph.edges(data=True), key=lambda x: x[2]["weight"], reverse=False)
        graph.remove_edge(edges[0][0], edges[0][1])
    #return the clusters and the new graph
    return nx.algorithms.community.greedy_modularity_communities(graph, cutoff=m, best_n=m), graph

def getCentroide(nodes, stations):
    """get the centroide of a list of nodes"""
    #find the average lat and lon of the nodes
    print("Nodes in getCentroide: ",nodes)
    lat = 0
    lon = 0
    for node in nodes:
        lat += stations.loc[stations["station_id"] == node]["lat"].item()
        lon += stations.loc[stations["station_id"] == node]["lon"].item()
    lat /= len(nodes)
    lon /= len(nodes)
    return lat, lon

def getCenroideVector(nodes, simVectors):
    """get the centroide vector of a list of nodes"""
    #find the average vector of the nodes
    vector = np.zeros(24)
    for node in nodes:
        vector += simVectors[node[0]]
    vector /= len(nodes)
    return vector

def getCentroideWeigths(stations, simVectors, clusters):
    weigths =dict()
    for cluster in cluster:
        print("cluster: ", cluster)
        lat, lon = getCentroide(cluster, stations)
        simVector = getCenroideVector(cluster, simVectors)
        for station in simVectors:
            lat2 = stations.loc[stations["station_id"] == station]["lat"].item()
            lon2 = stations.loc[stations["station_id"] == station]["lon"].item()
            if station not in cluster:
                sim = pearsonr(simVector, simVectors[station])
                dist = haversine((lat, lon), (lat2, lon2))
                weigths[(cluster, station)] = sim.statistic+math.log10(0.25/dist)
                print (f'clusterX {cluster} and station {station} have weigth: {weigths[(cluster, station)]}, and distance: {dist}')
    return weigths

def updateEdges(clusters, stations, simVectors):
    #create a centroid for each cluster, remove all stations i a cluster from stations and add the centroids to stations
    print(clusters)
    for cluster in clusters:
        print(cluster)
        print (stations)
        stations = stations.drop(cluster)
        weigths = getCentroideWeigths(stations, simVectors)
        stations.append(cluster)
    #calculate the weigths between the centroids and the stations in stations list
    weigths = getCentroideWeigths(stations, simVectors)


def agglomarativeClustering(graph, simVectors, stations):
    graph_full = graph.copy()
    unconnected_nodes = set(graph_full.nodes())
    connected_nodes = set()
    #remove all edges from the graph
    graph.remove_edges_from(graph.edges())
    edges = sorted(graph_full.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)
    #add edges to the graph, until there are m clusters
    print(edges)
    while edges[0][2]["weight"] > 0.9:
        print("hello")
        graph.add_edge(edges[0][0], edges[0][1], weight= edges[0][2]["weight"])
        if (edges[0][0] in connected_nodes):
            connected_nodes.add(edges[0][0])
        if (edges[0][1] in connected_nodes):
            connected_nodes.remove(edges[0][1])
        connected_nodes.add(edges[0][0])
        connected_nodes.add(edges[0][1])
        edges.pop(0)
    #return the clusters and the new graph
    edges = updateEdges(nx.algorithms.components.connected_components(graph), stations, simVectors)
    return  nx.algorithms.components.connected_components(graph), graph

def main():
    graph, simVectors, stations = getGE()
    #plot the graph using networkx
    options = {
    'node_size': 25,
    'width': 1,
    }


    pos=nx.get_node_attributes(graph,'pos')
    ax= nx.draw(graph, pos, **options)
    plt.show()

    m = 200
    clusters = [{2347.0, 589.0}, {392, 443}, {401, 507, 423}, {491, 483, 495}, {432, 578, 518}, {441, 452}, {576, 577, 545, 609, 547, 448, 527, 599, 2328, 2330, 478}, {2332, 500, 2334}, {489, 739, 2308, 437}, {474, 618, 619}, {410, 399}, {481, 1101, 414}, {549, 396, 557, 526, 1023}, {434, 502}, {625, 387, 430}, {400, 530, 469, 389, 476}, {627, 572, 445, 559}, {523, 574}, {453, 405}, {480, 522, 381}, {624, 586}, {558, 449, 1755, 2329}, {505, 471}, {550, 462}, {620, 622, 556, 446}, {534, 479}, {617, 421}, {472, 407}, {508, 413, 590}, {568, 435, 748}, {509, 573}, {2280, 623, 390, 615}, {542, 551}, {2339, 475}, {388, 587, 588, 548}, {514, 506}, {442, 597}, {584, 473, 459}, {611, 787, 571}, {493, 598, 455}, {458, 415}, {431, 406, 487}, {398, 439}, {403, 564, 535}, {408, 377}, {426, 450, 519}, {496, 580}, {521, 385, 412}, {594, 612}, {626, 746}, {427, 613}, {537, 2337}, {498, 2270}, {411, 742}, {484, 429}, {488, 540}, {404, 511}, {744, 607}, {600, 735}, {970, 460}, {581, 583}, {608, 433}, {616, 541}, {425, 596, 382}]     #change the graph to include the clusters, and the stations in the clusters
    
    dgraph = nx.Graph()
    colors = dp.get_colors(len(clusters))
    for index, row in stations.iterrows():
        for cluster in clusters:
            if row["station_id"] in cluster:
                graph.add_node(row["station_id"], pos=(row["lon"],row["lat"]), color= colors[clusters.index(cluster)])
                print( "station: ", row["station_id"], " is in cluster: ", clusters.index(cluster))
                break
        else :
            graph.add_node(row["station_id"], pos=(row["lon"],row["lat"]), color= (0,0,0))
            print( "station: ", row["station_id"], " is not in any cluster")
    
    colors = [node[1]['color'] for node in graph.nodes(data=True)]

    #plot the clusters
    pos=nx.get_node_attributes(graph,'pos')
    ax= nx.draw(graph, pos, node_color=colors, **options)
    plt.show()
    print("Custers are: ", clusters)

    #create and plot a voronoi diagram with ONE CELL per cluster each cluster
    vor = Voronoi(stations[["lon", "lat"]].values)
    #Color the voronoi diagram with the color of the cluster, black if the cell is not in any cluster
    
    
    #plot the voronoi diagram
    fig = voronoi_plot_2d(vor, show_vertices=False, show_points=True, line_colors='black', line_width=1, line_alpha=0.6, point_size=2)
    plt.show()

    
main()