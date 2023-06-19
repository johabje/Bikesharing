import matplotlib.pyplot as plt
import math
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
import json
import pandas as pd

station1 = "480.0.csv"
station2 = "460.0.csv"
station3 = "1023.0.csv"
mastation1 = "460_2022_9.csv"
mastation2 = "1023_2022_9.csv"

svr = open(f'NoClustering/results/SVR/with_avail/all/CO_RF_pred.json')
rf = open(f'NoClustering/results/with_avail/all/CO_RF_pred.json')
ma = open(f'NoClustering/results/MA/CO_MA_pred.json')
actual = open(f'NoClustering/results/with_avail/all/testY.json')


rf_pred = json.load(rf)
svr_pred = json.load(svr)
ma_pred = json.load(ma)
actual_pred = json.load(actual)


#make a new dictionary with the same keys as the other dictionaries, containing the mean absoulte error for each key
def MAE(CO_pred, testY=actual_pred):
    mae = dict()
    for key in CO_pred:
        try:
            mae[key] = str(round(mean_absolute_error(testY[key], CO_pred[key]), ndigits=4))
        except:
            #print('no prediction for ' ,key)
            x=1
    return mae
def RMSE(CO_pred, testY=actual_pred):
    rmse = dict()
    for key in CO_pred:
        try:
            rmse[key] = str(round(math.sqrt(mean_squared_error(testY[key], CO_pred[key])), ndigits=4))
        except:
            #print('no prediction for ' ,key)
            x=1
    return rmse

def MAE_ma(CO_pred, testY=actual_pred):
    new_dict = dict()
    mae = dict()
    for key, value in CO_pred.items():
        #split the key to only station id
        station_id = key.split('_')[0]
        new_dict[f'{station_id}.0.csv'] = value
        print(station_id)
        print(f'{station_id}.0.csv')
        #print(new_dict[f'{station_id}.0.csv'])
    for key in new_dict:
        try:
            mae[key] = str(round(mean_absolute_error(testY[key], new_dict[key]), ndigits=4))
        except:
            print('no prediction for ' ,key)
            x=1
    return mae
def RMSE_ma(CO_pred, testY=actual_pred):
    new_dict = dict()
    mae = dict()
    for key, value in CO_pred.items():
        #split the key to only station id
        station_id = key.split('_')[0]
        new_dict[f'{station_id}.0.csv'] = value
        print(station_id)
        print(f'{station_id}.0.csv')
        #print(new_dict[f'{station_id}.0.csv'])
    for key in new_dict:
        try:
            mae[key] = str(round(math.sqrt(mean_squared_error(testY[key], new_dict[key])), ndigits=4))
        except:
            print('no prediction for ' ,key)
            x=1
    return mae

rf_mae = MAE(rf_pred)
rf_rmse = RMSE(rf_pred)
svr_mae = MAE(svr_pred)
svr_rmse = RMSE(svr_pred)
ma_mae = MAE_ma(ma_pred)
ma_rmse = RMSE_ma(ma_pred)
print(ma_mae)

def latTexTable(rf_rmse, svr_rmse, ma_rmse):
    with open("NoClustering/table.tex", "w") as f:
        f.write('\\begin{table}[ht]\n\\caption{RMSE for each station}\n\\centering\n')
        f.write('\\begin{tabular}{@{}c c@{}}\n\t\\toprule\n\t{\\bfseries Station-Id} & {\\bfseries RF-A} & {\\bfseries SVR-A} &{\\bfseries MA} \\\\\n\t\\midrule\n\t')
        f.write("\\\\ \n\t".join(["{} & {} & {} & {}".format(_k.split('.')[0], rf_rmse[_k], svr_rmse[_k], ma_rmse[_k]) for _k, _v in sorted(rf_rmse.items())]))
        f.write('\\\\\n\t\\bottomrule\n\\end{tabular}\n\\label{table:nonlin}\n\\end{table}')


#latTexTable(rf_mae, svr_mae, ma_mae)

def winners(rf_mae,svr_mae, ma_mae):
    #we want to assigne each station according to the best model
    #returning a dictionary with the model as key and the station as value
    winners = dict()
    for key in rf_mae:
        if rf_mae[key] < svr_mae[key] and rf_mae[key] < ma_mae[key]:
            winners[key.split('.')[0]] = 'RF-A'
        elif svr_mae[key] < rf_mae[key] and svr_mae[key] < ma_mae[key]:
            winners[key.split('.')[0]] = 'SVR-A'
        elif ma_mae[key] < rf_mae[key] and ma_mae[key] < svr_mae[key]:
            winners[key.split('.')[0]] = 'MA'
        else:
            winners[key.split('.')[0]] = 'Tie'
    print(f'RF-A: {list(winners.values()).count("RF-A")}')
    print(f'SVR-A: {list(winners.values()).count("SVR-A")}')
    print(f'MA: {list(winners.values()).count("MA")}')
    print(f'Tie: {list(winners.values()).count("Tie")}')

    return winners

winner = winners(rf_mae, svr_mae, ma_mae)
winner = winners(rf_rmse, svr_rmse, ma_rmse)
print(winner)

from matplotlib.legend_handler import HandlerTuple
import numpy as np
#we want to plot wich model is the best for each station, and sort the stations by various parameters, staring with mean checkouts
def plot_winners(winners):
    for key in winners:
        list = actual_pred[f'{key}.0.csv']
        mean = sum(list)/len(list)
        var = np.var(list)
        winners[key] = [winners[key], mean, var]
    sorted_winners = sorted(winners.items(), key=lambda x: x[1][1], reverse=True)
    #plot the winners
    x = [i[1][2] for i in sorted_winners]
    y = [i[1][1] for i in sorted_winners]
    z= []
    colors = {'RF-A': 'red', 'SVR-A': 'blue', 'MA': 'green'}
    labels = []
    labels.append(plt.Line2D([], [], marker='o', color='red', label='RF-A'))
    labels.append(plt.Line2D([], [], marker='o', color='blue', label='SVR-A'))
    labels.append(plt.Line2D([], [], marker='o', color='green', label='MA'))

    z = []
    for i in sorted_winners:
        model = i[1][0]
        if model in colors:
            z.append(colors[model])
            

    plt.scatter(x, y, c=z)
    plt.xlabel("Variance")
    plt.ylabel("Mean Checkouts")
    plt.legend(handles=labels, loc='upper right')
    plt.show()

plot_winners(winner)



def plot_pred(rf_pred, svr_pred, ma_pred, actual_pred):

    station_405_rf = rf_pred[station2]
    station_405_svr = svr_pred[station2]
    station_405_ma = ma_pred[mastation1]
    station_405_actual = actual_pred[station2]
    plt.plot(station_405_rf, label="RF-A")
    plt.plot(station_405_svr, label="SVR-A")
    plt.plot(station_405_ma, label="MA")
    plt.plot(station_405_actual, label="Actual",linewidth=int(2), color=str('black'))

    plt.legend()
    plt.xlabel("Hour")
    plt.ylabel("Number of Check-outs")
    plt.show()

    station_405_rf = rf_pred[station3]
    station_405_svr = svr_pred[station3]
    station_405_ma = ma_pred[mastation2]
    station_405_actual = actual_pred[station3]
    plt.plot(station_405_rf, label="RF-A")
    plt.plot(station_405_svr, label="SVR-A")
    plt.plot(station_405_ma, label="MA")
    plt.plot(station_405_actual, label="Actual",linewidth=int(2), color=str('black'))

    plt.legend()
    plt.xlabel("Hour")
    plt.ylabel("Number of Check-outs")
    plt.show()
