import os
import pandas as pd
import json
import numpy as np

def trainMA(X_train, Y_train, station, window_size=3):
    moving_average = Y_train.rolling(window=window_size).mean().iloc[-1]
    print(f"Training for station {station}")
    return moving_average


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
    
    stations=os.listdir(f"Data/Dataset_clusters/{month}")
    
    return stations


def getAreaData(area, month):
    data = pd.read_csv(f"Data/Dataset_clusters/{month}/{area}", index_col=0)
    data['count_last_hour'] = data['count_last_hour'].fillna(0)
    return data

# Other functions remain the same

def Test_train_month(pred_periods, month, window_size=10):
    """Implements the moving average prediction model for the given number of periods"""

    areas = getAreas(month)
    models = dict()
    testX = dict()
    testY = dict()
    CO_pred = dict()
    
    for station in areas:
        print("Now starting station ", station)
        data = getAreaData(station, month)
        CO_pred[station] = []
        
        test_data = data.iloc[-pred_periods:,:]
        
        print(test_data)
        X_test, Y_test = prepTestData(test_data)
        testX[station], testY[station] = X_test, list(Y_test)
        print(X_test)
        print(X_test.info())

        train_data = data.head(-(pred_periods-1))
        X_train = train_data.drop(columns=["count" ], inplace=False)
    
        Y_train = train_data["count"]

        models[station] = trainMA(X_train, Y_train, station,window_size)
        print("Area ", areas.index(station), " has been trained")
        

    # for i in range(0, pred_periods):
    #     print(i)
    #     for station in areas:
    #         moving_average = models[station]
    #         CO_pred[station].append(moving_average)
    #         testX[station]["count_last_hour"][i + 1] = moving_average
    
    for i in range(0, pred_periods):
        print(i)
        for station in areas:
            moving_average = models[station]
            CO_pred[station].append(moving_average)
            
            # Update the moving average with the actual value from the previous time step
            if i > 0:
                moving_average = (moving_average * (window_size - 1) + testY[station][i - 1]) / window_size
                moving_average = (moving_average * (window_size - 1) + testY[station][i - 1]) / window_size

                
            testX[station]["count_last_hour"][i + 1] = moving_average
            
  
    
  
            
            
    with open(f'Clustering/results/{month}/CO_MA_norm_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
    with open(f'Clustering/results/{month}/testY_norm.json', 'w') as fp:
        json.dump(testY, fp)

months = ["06_norm"]

for month in months:
    Test_train_month(24, month)
