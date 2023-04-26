
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
def mean_RMSE(CO_pred, testY):
    r2s = []
    for key in CO_pred:
        try:
            r2s.append(math.sqrt(mean_squared_error(testY[key], CO_pred[key])))
        except:
            #print('no prediction for ' ,key)
            x=1
    print( f'Mean RMSE is: {sum(r2s) / len(r2s)}')

f = open('archive/results3/CI_pred.json')
f2 = open('archive/results3/CO_RF_pred.json')
f3 = open('archive/results3/testY.json')
f4 = open('archive/results3/CI_true.json')

#f5 = open('results/CO_RF_pred.json')
# returns JSON object as 
# a dictionary
CI_pred = json.load(f)
CO_pred = json.load(f2)
testY = json.load(f3)
CI_true = json.load(f4)

#CO_RF_pred = json.load(f5)

print("RF-Avail")
mean_MAE(CO_pred, testY)
mean_r2(CO_pred, testY)
mean_RMSE(CO_pred, testY)
print("----------------------------------------")

print("CI-RF-Avail")
mean_MAE(CI_pred, CI_true)
print(mean_r2(CI_pred, CI_true))
mean_RMSE(CI_pred, CI_true)
print("----------------------------------------")
'''
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

station_405_pred = CO_pred["405"]
station_405_true = testY["405"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()


station_405_pred = CO_pred["480"]
station_405_true = testY["480"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()

station_405_pred = CO_pred["560"]
station_405_true = testY["560"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()


df = pd.read_csv("data/tripdata/2022/08.csv")

top_ten = df['start_station_id'].value_counts()[:10].sort_values(ascending=False)
b_ten = df['start_station_id'].value_counts().sort_values(ascending=True)[:10]


b_ten = list(b_ten.index)
top_ten = list(top_ten.index)
print(b_ten)
print(top_ten)

def mean_r2_10(CO_pred, testY, top):
    r2s = []
    for key in map(str, top):
        try:
            r2s.append(r2_score(testY[key], CO_pred[key]))
        except:
            #print('no prediction for ' ,key)
            x=1
    print( f'Mean r2 is: {sum(r2s) / len(r2s)}')
    

def mean_MAE_10(CO_pred, testY, top):
    r2s = []
    for key in map(str, top):
        try:
            r2s.append(mean_absolute_error(testY[key], CO_pred[key]))
        except:
            #print('no prediction for ' ,key)
            x=1
    print( f'Mean MAE is: {sum(r2s) / len(r2s)}')

def mean_RMSE_10(CO_pred, testY, top):
    r2s = []

    for key in map(str, top):
        try:
            r2s.append(math.sqrt(mean_squared_error(testY[key], CO_pred[key])))
        except:
            #print('no prediction for ' ,key)
            x=1
    print( f'Mean RMSE is: {sum(r2s) / len(r2s)}')

print("top 10")
mean_MAE_10(CO_pred, testY, top_ten)
mean_r2_10(CO_pred, testY, top_ten)
mean_RMSE_10(CO_pred, testY, top_ten)
print("--------------------------")
print("worst ten")
mean_MAE_10(CO_pred, testY, b_ten)
mean_r2_10(CO_pred, testY, b_ten)
mean_RMSE_10(CO_pred, testY, b_ten)
print("--------------------------")