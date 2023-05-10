from sklearn.ensemble import RandomForestRegressor
import os
import pandas as pd
import json

from sklearn.model_selection import RandomizedSearchCV

def trainRandom(X_train, Y_train, station):

    # Create the parameter grid based on the results of random search 
    # Create a based model
    rf = RandomForestRegressor()
    # Instantiate the grid search model
    random_grid= {'bootstrap': [True, False],
 'max_depth': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None],
 'max_features': ['auto', 'sqrt'],
 'min_samples_leaf': [1, 2, 4],
 'min_samples_split': [2, 5, 10],
 'n_estimators': [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]}
    rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)

    rf.fit(X_train, Y_train)

    print(f"training for station {station}")
    return rf

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
            #drop all colums named something with dock
            month_data = month_data.drop(columns=[col for col in month_data.columns if 'dock' in col])
        except:
            continue
        print(month_data.info())
        print(data.info())
        month_data['count_last_hour'] = month_data['count_last_hour'].fillna(0)
        data = data.append(month_data)
        #drop all rows with NaN
        data = data.dropna()
        data = data.iloc[:-1]
    return data


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
            testX[station]["count_last_hour"][i+1]= prediction[0]
        
    with open(f'NoClustering/results/with_avail/all/CO_RF_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
    with open(f'NoClustering/results/with_avail/all/testY.json', 'w') as fp:
        json.dump(testY, fp)


months = ["06", "07", "08", "09"]


Test_train_month(24, months)