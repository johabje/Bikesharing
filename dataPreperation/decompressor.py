import pandas as pd


def openfile(number):
    return open("./gbfs-oslo-station-station-2020-2022_station-status-000000000000").read()

def decompress(data):
    return snappy.uncompress(data)

def importToCsv(filenumber):
    from fastavro import reader
    with open('gbfs-oslo-station-station-2020-2022/station-status-{}'.format(filenumber), 'rb') as fo:
        avro_reader = reader(fo)
        records = [record for record in avro_reader]
        df = pd.DataFrame.from_records(records)


    #print(df.info())
    df = df.drop(columns=['system_id', "execution_timestamp",'execution_time_utc', '__tablename__', ])
    df.drop(df[df['is_renting'] == 0].index, inplace = True)
    df.drop(df[df['is_installed'] == 0].index, inplace = True)
    df.drop(df[df['is_returning'] == 0].index, inplace = True)
    df = df.drop(columns=[ 'is_renting', 'is_installed','is_returning', "name",'lat', 'lon', 'capacity'])

    #print(df.info())

    df.to_csv('cleanCSVgbfs/{}.csv'.format(filenumber))
    print("saved filenumber {} to folder".format(filenumber))

#importToCsv('000000000000')

for i in range(0,1031):
    importToCsv(f"{i:012}")