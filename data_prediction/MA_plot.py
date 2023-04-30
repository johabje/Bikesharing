import json
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import math
import matplotlib.pyplot as plt
import pandas as pd

month = "06_norm"
months = "6"

# Other functions remain the same

f2 = open(f'data_prediction/results/{month}/CO_MA_norm_pred.json')  # Changed from RF to MA
f3 = open(f'data_prediction/results/{month}/testY_norm.json')  # Changed to testY_norm

CO_pred = json.load(f2)
testY = json.load(f3)

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





print("MA-Avail")
mean_MAE(CO_pred, testY)
mean_r2(CO_pred, testY)
mean_RMSE(CO_pred, testY)
print("----------------------------------------")

station_405_pred = CO_pred[f"3_2022_{months}.csv"]
station_405_true = testY[f"1_2022_{months}.csv"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()

station_405_pred = CO_pred[f"45_2022_{months}.csv"]
station_405_true = testY[f"45_2022_{months}.csv"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()

station_405_pred = CO_pred[f"404_2022_{months}.csv"]
station_405_true = testY[f"404_2022_{months}.csv"]
plt.plot(station_405_pred, label="Prediction")
plt.plot(station_405_true, label="Actual")

plt.legend()
plt.xlabel("Hour")
plt.ylabel("Number of Check-outs")
plt.show()
