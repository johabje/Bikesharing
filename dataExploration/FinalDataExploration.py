from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os
import seaborn as sns

station_1_id = 2330

station_2_id = 666
def getAllData(station):
    station_df = pd.DataFrame()
    months = os.listdir("Data/Dataset_NoClusters/with_avail")
    #print(years)
        #if year =="2022":
         #  months.remove("10")
          # months.remove("9")
           #months.remove("8")
           #months.remove("7")
           #months.remove("6")
    for month in months:
        try:
          
            print(f'Data/Dataset_NoClusters/with_avail/{month}/{station}_2022_{month[-1]}.csv')
            df_temp = pd.read_csv(f'Data/Dataset_NoClusters/with_avail/{month}/{station}.0.csv')
            print(df_temp)
        except:
            print(f"No Records for {month}")
            continue
        station_df=pd.concat([station_df, df_temp], ignore_index=True)
    #station_df.rename(columns = {'count':'malvar'}, inplace = True)
    #print(station_df["dateTime"])
   
    return station_df


df_2330 =getAllData(2330)
df_405 = getAllData(405)
#print(df_2330["vind"])
#avrage demand by day
def meanPerhour():
    labels = []
    for i in range(0,24):
        h=str(i)
        labels.append(f'{h.zfill(2)}')
    plt.subplot(1, 2, 1)
    df_2330.groupby(pd.cut(df_2330.hour, np.linspace(0,24,25))).malvar.mean().plot.bar(ylabel='Mean Check-outs')

    plt.title("station 2330")
    ax = plt.gca()
    ax.set_xticklabels(labels)

    plt.subplot(1, 2, 2)
    df_405.groupby(pd.cut(df_405.hour, np.linspace(0,24,25))).malvar.mean().plot.bar(ylabel='Mean Check-outs')
    plt.title("station 405")
    ax = plt.gca()
    ax.set_xticklabels(labels)

    plt.tight_layout()
    plt.show()

#meanPerhour()

def meanPerDay():
    labels = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    plt.subplot(1, 2, 1)
    df_2330.groupby(pd.cut(df_2330.weekday, 7)).malvar.mean().plot.bar(ylabel='Mean Check-outs per hour')
    plt.title("station 2330")
    ax = plt.gca()
    ax.set_xticklabels(labels)

    plt.subplot(1, 2, 2)
    df_405.groupby(pd.cut(df_405.weekday, 7)).malvar.mean().plot.bar(ylabel='Mean Check-outs per hour')
    plt.title("station 405")
    ax = plt.gca()
    ax.set_xticklabels(labels)

    plt.show()
#meanPerDay()

def ridesPerMonth():
    labels = []
    for i in range(1,13):
        h=str(i)
        labels.append(f'{h.zfill(2)}')
    plt.subplot(1, 2, 1)
    df_2330.groupby(pd.cut(df_2330.month, 12)).malvar.mean().plot.bar(ylabel='Mean Check-outs per hour')

    plt.title("station 1023")
    ax = plt.gca()
    ax.set_xticklabels(labels)

    plt.subplot(1, 2, 2)
    df_405.groupby(pd.cut(df_405.month, 12)).malvar.mean().plot.bar(ylabel='Mean Check-outs per hour')

    plt.title("station 460")
    ax = plt.gca()
    ax.set_xticklabels(labels)
    plt.show()

#ridesPerMonth()

def ridesPerTemp():
    plt.subplot(1, 2, 1)
    df_2330.groupby(pd.cut(df_2330.temp, np.linspace(-15,31.5,200))).malvar.mean().plot.bar(ylabel='Mean Check-outs per hour', xlabel="Temperature")
    
    plt.title("Station 2330")
    ax = plt.gca()
    ax.set_xticklabels(np.around(np.arange(-15,32,47/199), 0))
    every_nth=10
    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
    plt.subplot(1, 2, 2)
    df_405.groupby(pd.cut(df_405.temp, np.linspace(-15,31.5,200))).malvar.mean().plot.bar(ylabel='Mean Check-outs per hour', xlabel="Temperature")
    plt.title("Station 405")
    ax = plt.gca()
    ax.set_xticklabels(np.around(np.arange(-15,32,47/199), 0))
    every_nth=10
    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
    plt.show()

    #plt.bar(huha, range= [-15, 32])

    #df_405.groupby(pd.cut(df_2330.temp, np.linspace(-14.6,31.5,46) )).malvar.mean().plot(kind="hist")
    
    #sns.histplot(data=df_temp['malvar'], x=range(-14,))


    plt.show()

#ridesPerTemp()

def correlations():
    
    df_2330.rename(columns = {'Nedbør (1 t)':'precipitation', 'Middelvind':'wind', "Lufttemperatur":"temprature", "Skydekke": "cloud_cover"}, inplace = True)
    print(df_2330.info())
    first_column = df_2330.pop('count')
    df_2330.insert(0, 'count', first_column)
    df_2330.drop(columns=["dock_availability_1", "dock_availability_2"], inplace=True)
    corr2330 = df_2330.corr()
    
    sns.heatmap(corr2330, xticklabels= True, yticklabels= True, vmin=-1, vmax=1, cmap='BrBG')

    plt.title("Correlation matrix station 2330")
    plt.show()

    df_405.rename(columns = {'Nedbør (1 t)':'precipitation', 'Middelvind':'wind', "Lufttemperatur":"temprature", "Skydekke": "cloud_cover"}, inplace = True)
    
    print(df_405.info())
    first_column = df_405.pop('count')
    df_405.insert(0, 'count', first_column)
    df_405.drop(columns=["dock_availability_1"], inplace=True)
    corr405 = df_405.corr()
    print(corr405)
    sns.heatmap(corr405, xticklabels= True, yticklabels= True, vmin=-1, vmax=1, cmap='BrBG')
    plt.title("Correlation matrix station 405")
    plt.show()
correlations()

import math
def meanCountperHour():
    mean_counts = []
    for station in os.listdir("Data/Dataset_NoClusters/09"):
        
        df=pd.read_csv(f"fData/Dataset_NoClusters/09/{station}")
        mean_counts.append(df['count'].std())
    
    plt.hist(mean_counts, bins=60)
    plt.ylabel('Number of stations')
    plt.xlabel('std of hourly checkouts')
    plt.title("Histogram of hourly checkout standard deviation")
    plt.show() 

#meanCountperHour()   
#getAllData(station=405)