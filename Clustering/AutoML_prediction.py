from sklearn.ensemble import RandomForestRegressor
import os
import pandas as pd
import numpy as np
import json
from lightgbm import LGBMRegressor
import h2o
# h2o.init(max_mem_size='8G')
h2o.init()
from h2o.automl import H2OAutoML



def train(train_data):
    train_data = h2o.H2OFrame(train_data)
    
    x = train_data.columns
    y = "count"
    x.remove(y)
    
    
    

    aml = H2OAutoML(
                max_models=3,
                max_runtime_secs=100, 
                #max_runtime_secs_per_model=30
                project_name='regression', 
                stopping_metric="RMSE", 
                sort_metric="RMSE")
    aml.train(x=x, y=y, training_frame=train_data)
    
    return aml


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
        
        if i > 10:
            break
        
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
        
        models[station] = train(train_data)
 

    print("Total prediction perionds: ", pred_periods)
    
    for i in range(0,pred_periods):
      
        print("Prediction period: ", i)
     
        for station in areas:
            
            if station in models:
                print(testX[station].iloc[[i]])
                prediction = models[station].leader.predict(h2o.H2OFrame(testX[station].iloc[[i]]))
            
    
                
                print("prediction[0]: ", prediction)
            
                CO_pred[station].append(prediction[0])
        
                #testX[station]["count_last_hour"][i+1]= prediction[0]
                testX[station].loc[i+1, "count_last_hour"] = prediction[0]
                
                
            else:
                print(f"Model for station {station} not found.")
                continue

            
           

        
    with open(f'Clustering/results/Config 2/{month}/CO_RF_pred.json', 'w') as fp:
        json.dump(CO_pred, fp)
    with open(f'Clustering/results/Config 2/{month}/testY.json', 'w') as fp:
        json.dump(testY, fp)




months = ["06"]

for month in months:
    Test_train_month(24, month)


