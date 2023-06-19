from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor
import os
import pandas as pd
import json
from sklearn.svm import SVR
import warnings
warnings.filterwarnings("ignore")

import numpy as np
def trainRandom(X_train, Y_train, station):
    regressor = SVR(kernel='rbf', gamma=0.013 ,C=1)
    regressor.fit(X_train,Y_train)

    print(f"training for station {station}")
    return regressor

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

def getAreas(month):
    print(month[-1])

    stations=os.listdir(f"Data/Dataset_NoClusters/with_avail/{month[-1]}")
    print(stations)
    return stations

def getAreaData(area, months):
    data = pd.DataFrame()
    for month in months:
        try:
            month_data = pd.read_csv(f"Data/Dataset_NoClusters/with_avail/{month}/{area}", index_col=0)
            print(month_data.info())
            #drop all colums named something with dock
            month_data = month_data.drop(columns=[col for col in month_data.columns if 'dock' in col])
        except:
            continue
        print(month_data.info())
        print(data.info())
        month_data['count_last_hour'] = month_data['count_last_hour'].fillna(0)
        data = data.append(month_data)
        #drop all rows with NaN
        data = data.fillna(0)
        data.drop(columns=["month"], inplace=True)
        data = data.iloc[:-24*7]
    return data

def getFeatureImportance(station, model, X):
    importances = model.feature_importances_
    colums = list(X.columns)
    plt.barh(colums, importances)
    plt.show()

def Test_train_month(pred_periods, months):
    """Implements the random prediction model for the given number of periods"""

    areas = getAreas(months)
    models = dict()
    testX = dict()
    testY = dict()
    CO_pred = dict()
    CI_pred = dict()
    #print(getAllData(606).fillna(0))
    for station in areas:
        
        print("now startin station ",station)
        data = getAreaData(station, months)

        CO_pred[station] = []
        #CI_pred[station] = []
        #Test Train split
        #print(data.head(10))
        #print(data["Mean_close_count_last_hour"].head(2))
        test_data = data.iloc[-pred_periods:,:]
        
        print(test_data)
        #store test Data
        X_test, Y_test = prepTestData(test_data)

        testX[station], testY[station] = X_test, list(Y_test)
        print(X_test)
        print(X_test.info())

        train_data = data.head(-(pred_periods-1))
        X_train = train_data.drop(columns=["count" ], inplace=False)
    
        #print("length train dat", len(train_data))
        Y_train= train_data["count"]

        #train model
        models[station] = trainRandom(X_train,Y_train, station)
        """print("Area ", areas.index(station), " has been trained")
        if station == "460.0.csv" or station == "1023.0.csv":
            print("Feature importance for station ", station, ":")
            getFeatureImportance(station, models[station], X_train)
        """
    """stations = list(stations_ok)
    probDict = get_probability_dict("2022", "08")
    close_stations=stationDistancesMod(2022, 8, stations)"""
    for i in range(0,pred_periods):
        print(i)
        #1. perdict next row for each station
        #last_pred = dict()
        for station in areas:
            prediction = models[station].predict(testX[station].iloc[[i]])
            if prediction[0] < 0:
                prediction[0] = 0
            #print(testX[station].iloc[[i]])
            CO_pred[station].append(prediction[0])
            #print(prediction[0])
            #last_pred[station]=prediction[0]
            testX[station]["count_last_hour"][i+1]= prediction[0]
        
    with open(f'NoClustering/results/SVR/with_avail/all/CO_RF_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
    with open(f'NoClustering/results/SVR/with_avail/all/testY.json', 'w') as fp:
        json.dump(testY, fp)


months = ["06_2021", "07_2021", "08_2021", "09_2021","04_2022","05_2022","06_2022", "07_2022", "08_2022", "09_2022"]



Test_train_month(24, months)