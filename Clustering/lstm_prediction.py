from sklearn.ensemble import RandomForestRegressor
import os
import pandas as pd
import numpy as np
import json
from lightgbm import LGBMRegressor
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler






def train(X_train, Y_train):
    # Reshape input to be [samples, time steps, features]
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))

    # Define LSTM model
    model = Sequential()
    model.add(LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    
    model.fit(X_train, Y_train, epochs=100, batch_size=1, verbose=2)

    return model


def prepTestData(test_data):
    # print("len before: ", len(test_data))
    test_data.reset_index(drop=True,inplace=True)
    # print("len after: ", len(test_data))
    Y_test = test_data["count"]
    X_test = test_data.drop(columns=["count"], inplace=False)
    # X_test["count_last_hour"] = np.nan
    X_test["count_last_hour"] = 0
    # X_test["count_last_hour"] = None
    
    
    # X_test["count_last_hour"][0] = 0
    X_test.loc[0, "count_last_hour"] = 0

   
    return X_test, Y_test


config = "Config 2"
def getAreas(month):
    
    
    stations=os.listdir(f"Data/Dataset_clusters/Config 2/{month}")
    
    return stations


def getAreaData(area, month):
    data = pd.read_csv(f"Data/Dataset_clusters/Config 2/{month}/{area}", index_col=0)
    data['count_last_hour'] = data['count_last_hour'].fillna(0)
    return data

def Test_train_month(pred_periods, month):
    """Implements the random prediction model for the given number of periods"""

    areas = getAreas(month)
    models = dict()
    testX = dict()
    testY = dict()
    CO_pred = dict()
    X_test_transformed = dict()

    # Initialize a scaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    
    for i, station in enumerate(areas):
        print("total station numbers: ", len(areas))
        print("station number: ", i)
        data = getAreaData(station, month)
        CO_pred[station] = []
    
        test_data = data.iloc[-pred_periods:,:]
        
        X_test, Y_test = prepTestData(test_data)
        testX[station], testY[station] = X_test, list(Y_test)
 
        train_data = data.head(-(pred_periods-1))
        X_train = train_data.drop(columns=["count"], inplace=False)
        Y_train = train_data["count"]

        # Scale the data
        X_train = scaler.fit_transform(X_train)
        X_test_transformed[station] = scaler.transform(X_test)
        
        # train model
        models[station] = train(X_train, Y_train)
 
    print("Total prediction periods: ", pred_periods)
    for i in range(0, pred_periods):
        print("Prediction period: ", i)
        for station in areas:
            # Reshape input to be [samples, time steps, features]
            X_test_transformed[station] = np.reshape(X_test_transformed[station], (X_test_transformed[station].shape[0], 1, X_test_transformed[station].shape[1]))
            prediction = models[station].predict(X_test_transformed[station][i])
            CO_pred[station].append(prediction[0])
            if i+1 < pred_periods:
                X_test_transformed[station][i+1, 0] = prediction[0]
        
    with open(f'Clustering/results/Config 2/{month}/CO_RF_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
    with open(f'Clustering/results/Config 2/{month}/testY.json', 'w') as fp:
        json.dump(testY, fp)



months = ["06"]

for month in months:
    Test_train_month(24, month)

