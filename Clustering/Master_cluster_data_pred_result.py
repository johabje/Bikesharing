

from Cluster_adjecent_stations import main as setneigbours
from Dataset_Clusters import createDataset
from Agglomerativeclustering import main as cluster
from Cluster_pred_concat import Test_train_month as predRF
from Cluster_pred_concat_svm import Test_train_month as predSVM
from results_cluster import mean_RMSE, mean_MAE
from gbfs_hourly_to_clustered import main as setgbfs
import json
import os


configs = [[0.05,1], [0.1,2], [0.15,3], [0.2,4], [0.25,5], [0.3,6], [0.35,7], [0.4,8], [0.45,9], [0.5,10]]
months= ["06", "07", "08", "09",]
clusters = dict()
for config in configs:
    print("now starting config ", config[1], " with threshold ", config[0])
    cluster_ =  cluster(config[0], config[1])
    setgbfs(cluster_, f'Config {config[1]}')
    clusters[config[1]] = cluster_
    for month in months:
        createDataset(int(month), month, f"Config {config[1]}", cluster_)
        stations = os.listdir(f"Data/Dataset_Clusters/Config {config[1]}/{month}/")
        print(f'Config {config[1]} results in {len(stations)} areas')
        setneigbours(cluster_, "2022", month, int(month), f"Config {config[1]}")
    predRF(24, months, f"Config {config[1]}")
    predSVM(24, months, f"Config {config[1]}")

if not os.path.exists(f'Clustering/results/clusters'):
        os.makedirs(f'Clustering/results/clusters')

with open(f'Clustering/results/{config}/svm/CO_RF_pred.json', 'w') as fp:
    json.dump(clusters, fp)


