import pandas as pd
import glob

# Get a list of all csv files in the current directory
files = glob.glob("Data/gbfs_station_hour/Config 2/*.csv")

# Loop through all csv files
for file in files:
    # Load the csv file into a pandas DataFrame
    df = pd.read_csv(file)

    # Get the last index without NaN values
    last_index = df.dropna().index[-1]

    # Print the file name and last index without NaN values
    print(f"{file}: {last_index}")