from sklearn.ensemble import RandomForestRegressor
import os
import pandas as pd
import numpy as np
import json
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor



# def train(X_train, Y_train):
#     # set iterations to 1000
#     lgbm = LGBMRegressor(n_estimators=100)
#     #lgbm = LGBMRegressor()
#     lgbm.fit(X_train, Y_train)
#     return lgbm

def train(X_train, Y_train):
    # set iterations to 1000
    xgb = XGBRegressor(n_estimators=100)
    xgb.fit(X_train, Y_train)
    return xgb



def prepTestData(test_data):
   
    test_data.reset_index(drop=True,inplace=True)
    
    Y_test = test_data["count"]
    X_test = test_data.drop(columns=["count"], inplace=False)
  
    X_test["count_last_hour"] = 0

    

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

   
    
    for i, station in enumerate(areas):
        print("total station numbers: ", len(areas))
        print("station number: ", i)
        data = getAreaData(station, month)
        CO_pred[station] = []
    
        test_data = data.iloc[-pred_periods:,:]
        
      
        X_test, Y_test = prepTestData(test_data)
        testX[station], testY[station] = X_test, list(Y_test)
 

        train_data = data.head(-(pred_periods-1))
        X_train = train_data.drop(columns=["count" ], inplace=False)
    
   
        Y_train= train_data["count"]
        
        models[station] = train(X_train,Y_train)
 

    print("Total prediction perionds: ", pred_periods)
    
    for i in range(0,pred_periods):
      
        print("Prediction period: ", i)
     
        for station in areas:
            
            prediction = models[station].predict(testX[station].iloc[[i]])
            
        
            #CO_pred[station].append(prediction[0])
            CO_pred[station].append(float(prediction[0]))

       
    
            testX[station].loc[i+1, "count_last_hour"] = prediction[0]

        
    with open(f'Clustering/results/Config 2/{month}/CO_RF_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
    with open(f'Clustering/results/Config 2/{month}/testY.json', 'w') as fp:
        json.dump(testY, fp)




months = ["06"]

for month in months:
    Test_train_month(24, month)


