import json

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import math
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np


def mean_r2(CO_pred, testY):
    r2s = []
    for key in CO_pred:
        try:
            r2s.append(r2_score(testY[key], CO_pred[key]))
        except:
            #print('no prediction for ' ,key)
            x=1
    r2s.sort()
    r2s.pop(0)
    print( f'Mean r2 is: {sum(r2s) / len(r2s)}')
    #r2s.remove(-70.05087536729536)
    plt.plot(r2s)
    plt.show()
    

def mean_MAE(CO_pred, testY):
    r2s = []
    for key in CO_pred:
        try:
            r2s.append(mean_absolute_error(testY[key], CO_pred[key]))
        except:
            #print('no prediction for ' ,key)
            x=1
    #print( f'Mean MAE is: {sum(r2s) / len(r2s)}')
    return sum(r2s) / len(r2s)

def mean_RMSE(CO_pred, testY):
    r2s = []
    for key in CO_pred:
        try:
            r2s.append(math.sqrt(mean_squared_error(testY[key], CO_pred[key])))
        except:
            #print('no prediction for ' ,key)
            x=1
    return sum(r2s) / len(r2s)

#function to calculate the RRMSE for each area
def calculate_rrmse(actual, predicted):
    
    # Convert actual and predicted values to numpy arrays
    actual = np.array(actual)
    predicted = np.array(predicted)

    # Calculate mean squared error (MSE)
    mse = np.mean((predicted - actual) ** 2)

    # Calculate range of target variable
    target_range = np.max(actual) - np.min(actual)
    if target_range == 0:
        return 0
    # Calculate relative root mean squared error (RRMSE)
    rrmse = np.sqrt(mse) / target_range
    return rrmse

def area_rrmse(CO_pred, testY):
    r2s = []
    for key in CO_pred:
        try:
            r2s.append(calculate_rrmse(testY[key], CO_pred[key]))
        except:
            #print('no prediction for ' ,key)
            x=1
    return sum(r2s) / len(r2s)


configs = os.listdir('Clustering/results/')
configs.remove("clusters")

results = dict()
for config in configs:
    f2 = open(f'Clustering/results/{config}/rf/CO_RF_pred.json')
    f3 = open(f'Clustering/results/{config}/rf/testY.json')
    CO_pred = json.load(f2)
    testY = json.load(f3)
    RMSE = mean_RMSE(CO_pred, testY)
    MAE = mean_MAE(CO_pred, testY)
    mean_CO = area_rrmse(CO_pred, testY)
    arr = os.listdir(f'Data/Dataset_clusters/{config}/09/')
    print(f'{config}: ', "RMSE: ",RMSE, " MAE: ", MAE, " Number of areas: ", len(arr), " ", mean_CO)
    
    results[config] = [mean_CO, MAE, len(arr)]

#plot the RMSE point on the y-axis and the number of clusters on the x-axis
#plot the MAE on the y-axis and the number of clusters on the x-axis
plt.figure()
plt.title("RMSE")
plt.xlabel("Number of areas")
plt.ylabel("rRMSE")
#plot one point for each config
for key in results:
    plt.scatter(results[key][2], results[key][0], color='blue')

plt.gca().set_facecolor('white')
#set point color to blue
plt.show()


"""

#f5 = open('results/CO_RF_pred.json')
# returns JSON object as 
# a dictionary



#CO_RF_pred = json.load(f5)

"""
print("RF-Avail")
mean_MAE(CO_pred, testY)
mean_r2(CO_pred, testY)
mean_RMSE(CO_pred, testY)
print("----------------------------------------")

