import os
import pandas as pd

dataPath = "Data/Dataset_clusters/06/"
treatedDataPath= "Data/Dataset_clusters/06_norm/"

colums_numerical = ["Nedbør (1 t)", "Lufttemperatur", "Middelvind","Skydekke" ]
colums_categorical_nominal = []
colums_categorical_ordinal = [""]

files = os.listdir(dataPath)
print(files)
for file in files:
    #normalize numerical data
    df = pd.read_csv(dataPath + file, index_col=0)
    print(df.head(3))
    for column in colums_numerical:
        df[column] = (df[column] - df[column].mean()) / df[column].std()

    #store normalized dataset
    df.to_csv(treatedDataPath + file)


    
