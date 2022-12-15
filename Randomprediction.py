import pandas as pd
from sklearn.metrics import r2_score
from sklearn import metrics
from sklearn.metrics import mean_squared_error
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from numpy import random
from time import time
import calendar
from datetime import datetime
import os
from sklearn.ensemble import RandomForestRegressor
from FinalDataExploration import getAllData
from funWithPlots import findAllStations
from CheckInPerd import get_probability_dict
import json


Forest = RandomForestRegressor(random_state = 666, n_estimators = 500)

def rmsle(y, y_):
    log1 = np.nan_to_num(np.array([np.log(v + 1) for v in y]))
    log2 = np.nan_to_num(np.array([np.log(v + 1) for v in y_]))
    calc = (log1 - log2) ** 2
    return np.sqrt(np.mean(calc))

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

def mae(y, y_):
    return mean_absolute_error(y, y_, multioutput='raw_values')

#dicttest = dict({"hei":2, "balle":2})
#with open('results/CI_pred.json', 'w') as fp:
 #       json.dump(dicttest, fp)

def feature_importance(trained_model, columns):
    """"returns imortance of each feature for a model"""
    importances = trained_model.feature_importances_
    #
    # Sort the feature importance in descending order
    #
    sorted_indices = np.argsort(importances)[::-1]
    
    feat_labels = columns
    importances = pd.DataFrame(importances, columns)
    
    return importances

def trainRandom(X_train, Y_train, station):
    t0 = time()
    # Create the parameter grid based on the results of random search 
    param_grid = {
    'bootstrap': [True],
    'max_depth': [90, 100, 110],
    'max_features': [2, 3,4,8],
    'min_samples_leaf': [3, 4, 5],
    'n_estimators': [ 200, 300, 1000]
}
    # Create a based model
    rf = RandomForestRegressor()
    # Instantiate the grid search model
    
    
    rf.fit(X_train, Y_train)
    
    train_time = time() - t0
    
    print(f"training for station {station}, took {train_time}")
    return rf
    test_pred = Forest.predict(X_test)

    r2 = r2_score(Y_test, test_pred)
    print(Y_test)
    
    plt.plot(Y_test.values, label="GT")
    plt.plot(test_pred, label="RF")
    plt.title(f'Ground truth VS prediction station {station}')
    plt.legend()
    plt.show()
    
    root_mean_squared_log_error = rmsle(Y_test, test_pred)
    print ("r2_score of testing set is {}".format(r2))
    print ("Root mean squared log error is {}".format(root_mean_squared_log_error))
    print ("mean absolute error is {}".format(mae(Y_test, test_pred)))
    mse = mean_squared_error(Y_test, test_pred)
    improtances = feature_importance(Forest, X_train.columns)
    return improtances, mse, root_mean_squared_log_error, r2


def Average(lst):
    return sum(lst) / len(lst)

def stationDistancesMod(year, month, okstations):
    from haversine import haversine
    stations_dist = dict()
    #dict with stations, containig all stations within 500 meters, shuld be sorted by distance
    stations = findAllStations(year, month)
    for index, row in stations.iterrows():

        #print(row)
        lat = row["lat"]
        lon = row["lon"]
        id = row["station_id"]
        close_stations = []
        for index2, row2 in stations.iterrows():
            id2 = row2["station_id"]
            if int(id2) in okstations:
                if int(id) in okstations:
                    if id == row2["station_id"]: continue
                    dist = haversine({lat, lon}, {row2["lat"], row2["lon"]})
                    if dist < 0.5:
                        close_stations.append([int(row2["station_id"]), dist])
        close_stations = sorted(close_stations, key=lambda x: x[1], reverse=False)
        print(close_stations)
        stations_dist[id] = [i[0] for i in close_stations]
        print(stations_dist)
        #print(stations_dist)
    return stations_dist

def getFeatureImportance(station, model, X):
    importances = model.feature_importances_
    colums = list(X.columns)
    plt.barh(colums, importances)
    plt.show()

def prepTestData(test_data):
    #print("len before: ", len(test_data))
    test_data.reset_index(drop=True,inplace=True)
    #print("len after: ", len(test_data))
    Y_test = test_data["count"]
    X_test = test_data.drop(columns=["count"], inplace=False)
    X_test["count_last_hour"] = None
    X_test["count_last_hour"][0] = 0
    #X_test["Mean_close_count_last_hour"] = None
    #X_test["Mean_close_count_last_hour"][0] = 0
    return X_test, Y_test

def predictCheckIns(prob_station, Y_dict, i, stations):
    count = 0
    for key in stations:
        count += Y_dict[key][i]*prob_station[key]
    return count

pd.options.mode.chained_assignment = None
def Main(pred_periods):
    stations = findAllStations(2022, 8)
    stations = list(stations["station_id"])
    stations.remove(602)
    stations_ok = list(stations)
    models = dict()
    testX = dict()
    testY = dict()
    CO_pred = dict()
    CI_pred = dict()
    
    close_stations=stationDistancesMod(2022, 8, stations)
    test = getAllData(2330).fillna(0)
    
    
    #print(getAllData(606).fillna(0))
    for station in stations:
        print("now startin station ",station)
        CO_pred[station] = []
        CI_pred[station] = []
        #Test Train split
        data = getAllData(station).fillna(0)
        if len(data) == 0:
            stations_ok.remove(station)
            print(station)
            continue
        #data.drop(columns=["Mean_close_count_last_hour"])
        #uncomment the line below to train without availability  
        #data = data.loc[:, ["nedør",'temp','vind','hour','count','count_last_hour','isHoliday','weekday','month', "Mean_close_count_last_hour"]]  
        #print(data.head(10))
        data.loc[data["vind"] == '-', "vind"] = 0
        data["vind"] = data["vind"].astype(float)
        data.rename(columns = {'nedør':'precipitation', 'vind':'wind'}, inplace = True)
        #print(data["Mean_close_count_last_hour"].head(2))
        test_data = data.iloc[-pred_periods:,:]
        print(test_data.index)
        #store test Data
        X_test, Y_test = prepTestData(test_data)
        testX[station], testY[station] = X_test, list(Y_test)
        print(X_test)
        #print(X_test.info())

        train_data = data.head(-(pred_periods-1))
        print(train_data)
        X_train = train_data.drop(columns=["count" ], inplace=False)
        #print(X_train.head(10))
        #print("length train dat", len(train_data))
        Y_train= train_data["count"]

        #train model
        models[station] = trainRandom(X_train,Y_train, station)
        print(stations.index(station))
        if station == 2330 or station == 405:
         
            getFeatureImportance(station, models[station], X_train)
        #uncomment to test on one station
        #break

    stations = list(stations_ok)
    probDict = get_probability_dict("2022", "08")
    close_stations=stationDistancesMod(2022, 8, stations)
    for i in range(0,pred_periods):
        print(i)
        #1. perdict next row for each station
        #last_pred = dict()
        for station in stations:
            prediction = models[station].predict(testX[station].iloc[[i]])
            #print(testX[station].iloc[[i]])
            CO_pred[station].append(prediction[0])
            #print(prediction[0])
            #last_pred[station]=prediction[0]
            testX[station]["count_last_hour"][i+1]= prediction[0]
            
        """
        for station in stations:
            close_counts = [ last_pred[c] for c in close_stations[station] ]
            print(close_counts)
            try:
                testX[station]["Mean_close_count_last_hour"][i+1] = sum(close_counts)/len(close_counts)
                print("Mean count should be: ", sum(close_counts)/len(close_counts))
                print("the list is: ", testX[station][i+1])
            except:
                #len = 0 means the station has no close station
                x=1
               """ 
        #2. perdict check-ins
       
        for station in stations: 
            prediction = predictCheckIns(probDict[station], CO_pred, i, stations)
            CI_pred[station].append(prediction)
        
        print(CI_pred[2330])
    with open('results3/CI_RF_pred.json', 'w') as fp:
        json.dump(CI_pred, fp)
    with open('results3/CO_RF_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
    with open('results3/testY.json', 'w') as fp:
        json.dump(testY, fp)


stations = findAllStations(2022, 8)
stationDistancesMod(2022, 8, stations)


Main(168)