from sklearn.ensemble import RandomForestRegressor
import os
import pandas as pd
import json

def trainRandom(X_train, Y_train, station):

    # Create the parameter grid based on the results of random search 
    # Create a based model
    
    rf = RandomForestRegressor()
    
    # Instantiate the grid search model
    
    rf.fit(X_train, Y_train)

    print(f"training for station {station}")
    return rf

def prepTestData(test_data):
    
    # print("len before: ", len(test_data))
    
    test_data.reset_index(drop=True,inplace=True)
    
    # print("len after: ", len(test_data))
    
    Y_test = test_data["count"]
    X_test = test_data.drop(columns=["count"], inplace=False)
    X_test["count_last_hour"] = None
    X_test["count_last_hour"][0] = 0
    
    # X_test["Mean_close_count_last_hour"] = None
    # X_test["Mean_close_count_last_hour"][0] = 0
    
    return X_test, Y_test

def getAreas(month):
    
    stations=os.listdir(f"Data/Dataset_clusters/{month}")
    
    return stations

def getAreaData(area, month):
    data = pd.read_csv(f"Data/Dataset_clusters/{month}/{area}", index_col=0)
    data['count_last_hour'] = data['count_last_hour'].fillna(0)
    return data



def Test_train_month(pred_periods, month):
    """Implements the random prediction model for the given number of periods"""

    areas = getAreas(month)
    models = dict()
    testX = dict()
    testY = dict()
    CO_pred = dict()
    CI_pred = dict()
    #print(getAllData(606).fillna(0))
    for station in areas:
        print("now starting station ",station)
        data = getAreaData(station, month)
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
        print("Area ", areas.index(station), " has been trained")
        

    """stations = list(stations_ok)
    probDict = get_probability_dict("2022", "08")
    close_stations=stationDistancesMod(2022, 8, stations)"""
    
    
    
    for i in range(0,pred_periods):
        print(i)
        #1. perdict next row for each station
        #last_pred = dict()
        for station in areas:
            
            prediction = models[station].predict(testX[station].iloc[[i]])
            #print(testX[station].iloc[[i]])
            
            CO_pred[station].append(prediction[0])
            
            #print(prediction[0])
            #last_pred[station]=prediction[0]
            testX[station]["count_last_hour"][i+1] = prediction[0]
        
    with open(f'Clustering/results/{month}/CO_RF_norm_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
        
    with open(f'Clustering/results/{month}/testY_norm.json', 'w') as fp:
        json.dump(testY, fp)

months = ["06_norm"]


for month in months:
    Test_train_month(24, month)