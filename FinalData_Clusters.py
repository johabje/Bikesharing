
# Testcase for 30 days of data
# 1. Read trip data for each cluster from tripdata_2022_08.csv
# 2. Add weather data to each record
# 3. Add weekday binary to each record
# 4. Add hour of day to each record
# 5. Add month to each record
# 6. Add year to each record

import pandas as pd
import datetime as dt


clusters = [{2347.0, 589.0}, {392, 443}, {401, 423}, {491, 483, 495}, {432, 578, 518}, {441, 452}, {576, 577, 545, 609, 547, 599, 2328, 2330, 478}, {2332, 500, 2334}, {489, 739, 2308, 437}, {618, 619}, {410, 399}, {481, 1101, 414}, {549, 396, 557, 526, 1023}, {434, 502}, {625, 387, 430}, {400, 530, 469, 389, 476}, {627, 572, 559}, {523, 574}, {453, 405}, {480, 522, 381}, {624, 586}, {558, 449, 1755, 2329}, {505, 471}, {550, 462}, {556, 446}, {534, 479}, {617, 421}, {472, 407}, {508, 413, 590}, {435, 748}, {509, 573}, {2280, 623, 390, 615}, {542, 551}, {2339, 475}, {587, 588}, {514, 506}, {442, 597}, {584, 459}, {611, 787, 571}, {620, 622}, {493, 598, 455}, {458, 415}, {431, 406, 487}, {398, 439}, {403, 564}, {408, 377}, {388, 548}, {426, 450, 519}, {496, 580}, {521, 412}, {594, 612}, {626, 746}, {448, 527}, {427, 613}, {537, 2337}, {498, 2270}, {411, 742}]

tripdata = pd.read_csv("tripdata/2022/08.csv", parse_dates=True)
tripdata["started_at"] = pd.to_datetime(tripdata["started_at"])
tripdata["count"] = 1
tripdata.drop(columns=["ended_at", "start_station_name", "end_station_id", "end_station_name", "start_station_description","end_station_description","duration", "start_station_latitude" , "start_station_longitude",  "end_station_latitude",  "end_station_longitude" ], inplace=True)
tripdata.set_index('started_at', inplace=True)
print(tripdata)

def getTripData(stations, tripData, startTime, endTime):
    #for each station in the cluster
    counts = dict()
    for station in stations:
        #slice the dataframe such that it only contains the station
        tripDatastation = tripData[tripData["start_station_id"] == station]
        tripDatastationDayHour = tripDatastation.groupby(pd.Grouper(freq='60Min')).count()
        tripDatastationDayHour.drop(columns=["start_station_id"], inplace=True)   
        counts[station] = tripDatastationDayHour
        #add rows to the end of the dataframe for the missing hours
        firstIndex = tripDatastationDayHour.index[0]
        lastIndex = tripDatastationDayHour.index[-1]
        #number of rows missing at the beginning
        missingRowsStart = (startTime - firstIndex).total_seconds() / 3600
        #number of rows missing at the end
        missingRowsEnd = (lastIndex - endTime).total_seconds() / 3600
        #add rows to the beginning of the dataframe for the missing hours where counbt = 0
        
        #add rows for the missing days
        
    return counts

startTime = dt.datetime(2022, 8, 1, 0, 0, 0)
endTime = dt.datetime(2022, 8, 31, 23, 59, 59)
count =getTripData([2347, 377], tripdata)

print(count)
