import os
import pandas as pd

dataPath = "Data/Dataset_clusters/06/"

colums_numerical = ["Nedbør (1 t)", "Lufttemperatur", "Middelvind","Skydekke" ]
colums_categorical_nominal = []
colums_categorical_ordinal = [""]

files = os.listdir(dataPath)

for file in files:
    #normalize numerical data
    df = pd.read_csv(dataPath + file, index_col=0)
    for column in colums_numerical:
        df[column] = (df[column] - df[column].mean()) / df[column].std()

    #store normalized dataset
    df.to_csv(dataPath + file)
    
