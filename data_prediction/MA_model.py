import os
import pandas as pd
import json
import numpy as np

def trainMA(X_train, Y_train, station, window_size=3):
    # Calculate the moving average for the given window size
    def moving_average(y, window_size):
        y_np = np.array(y)
        cumsum = np.cumsum(y_np)
        cumsum[window_size:] = cumsum[:-window_size] + y_np[window_size:] - y_np[:-window_size]
        return cumsum[window_size - 1:] / window_size

    # Calculate the moving average of the target variable (Y_train)
    Y_train_ma = moving_average(Y_train, window_size)

    print(f"training for station {station}")
    return Y_train_ma





def prepTestData(test_data):
    test_data.reset_index(drop=True,inplace=True)
    Y_test = test_data["count"]
    X_test = test_data.drop(columns=["count"], inplace=False)
    X_test["count_last_hour"] = None
    X_test.at[0, "count_last_hour"] = 0
    return X_test, Y_test


def getAreas(month):
    
    stations=os.listdir(f"Data/Dataset_clusters/{month}")
    
    return stations


def getAreaData(area, month):
    data = pd.read_csv(f"Data/Dataset_clusters/{month}/{area}", index_col=0)
    data['count_last_hour'] = data['count_last_hour'].fillna(0)
    return data



def Test_train_month(pred_periods, month, window_size=300):
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

        models[station] = trainMA(X_train, Y_train, station, window_size)
        print("Area ", areas.index(station), " has been trained")
        

    for i in range(0, pred_periods):
        print(i)
        for station in areas:
            recent_values = testY[station][max(-i-1, -window_size):] + CO_pred[station][max(-window_size+i+1, 0):]
            moving_average = np.mean(recent_values)
            CO_pred[station].append(moving_average)
            
            if i + 1 < pred_periods:
                testX[station]["count_last_hour"][i + 1] = moving_average
    
            
    with open(f'data_prediction/results/{month}/CO_MA_norm_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
    with open(f'data_prediction/results/{month}/testY_norm.json', 'w') as fp:
        json.dump(testY, fp)





months = ["06_norm"]

for month in months:
    Test_train_month(24, month)
