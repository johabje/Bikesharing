import json

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import math
import matplotlib.pyplot as plt
import pandas as pd



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
    print( f'Mean MAE is: {sum(r2s) / len(r2s)}')
    plt.plot(r2s)
    plt.show()
def mean_RMSE(CO_pred, testY):
    r2s = []
    for key in CO_pred:
        try:
            r2s.append(math.sqrt(mean_squared_error(testY[key], CO_pred[key])))
        except:
            #print('no prediction for ' ,key)
            x=1
    print( f'Mean RMSE is: {sum(r2s) / len(r2s)}')

month = "all"
months = "9"
config = "Config 2"

f2 = open(f'Clustering/results/{config}/{month}/CO_RF_pred.json')
f3 = open(f'Clustering/results/{config}/{month}/testY.json')


#f5 = open('results/CO_RF_pred.json')
# returns JSON object as 
# a dictionary

CO_pred = json.load(f2)
testY = json.load(f3)

#CO_RF_pred = json.load(f5)

print("RF-Avail")
mean_MAE(CO_pred, testY)
mean_r2(CO_pred, testY)
mean_RMSE(CO_pred, testY)
print("----------------------------------------")
'''
print("CI-RF-Avail")
mean_MAE(CI_pred, CI_true)
print(mean_r2(CI_pred, CI_true))
mean_RMSE(CI_pred, CI_true)
print("----------------------------------------")

print("RF")
mean_MAE(CO_RF_pred, testY)
mean_r2(CO_RF_pred, testY)
mean_RMSE(CO_RF_pred, testY)
print("----------------------------------------")

print("CI")
mean_MAE(CI_RF_pred, CI_true)
print(mean_r2(CI_RF_pred, CI_true))
mean_RMSE(CI_RF_pred, CI_true)
print("----------------------------------------")
'''


station_405_pred = CO_pred[f"1_2022_{months}.csv"]
station_405_true = testY[f"1_2022_{months}.csv"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()


station_405_pred = CO_pred[f"30_2022_{months}.csv"]
station_405_true = testY[f"30_2022_{months}.csv"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()

station_405_pred = CO_pred[f"787_2022_{months}.csv"]
station_405_true = testY[f"787_2022_{months}.csv"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()

