#This script is used to concat the gbfs data from all stations in a clusters

clusters = [{2347.0, 589.0}, {392, 443}, {401, 507, 423}, {491, 483, 495}, {432, 578, 518}, {441, 452}, {576, 577, 545, 609, 547, 448, 527, 599, 2328, 2330, 478}, {2332, 500, 2334}, {489, 739, 2308, 437}, {474, 618, 619}, {410, 399}, {481, 1101, 414}, {549, 396, 557, 526, 1023}, {434, 502}, {625, 387, 430}, {400, 530, 469, 389, 476}, {627, 572, 445, 559}, {523, 574}, {453, 405}, {480, 522, 381}, {624, 586}, {558, 449, 1755, 2329}, {505, 471}, {550, 462}, {620, 622, 556, 446}, {534, 479}, {617, 421}, {472, 407}, {508, 413, 590}, {568, 435, 748}, {509, 573}, {2280, 623, 390, 615}, {542, 551}, {2339, 475}, {388, 587, 588, 548}, {514, 506}, {442, 597}, {584, 473, 459}, {611, 787, 571}, {493, 598, 455}, {458, 415}, {431, 406, 487}, {398, 439}, {403, 564, 535}, {408, 377}, {426, 450, 519}, {496, 580}, {521, 385, 412}, {594, 612}, {626, 746}, {427, 613}, {537, 2337}, {498, 2270}, {411, 742}, {484, 429}, {488, 540}, {404, 511}, {744, 607}, {600, 735}, {970, 460}, {581, 583}, {608, 433}, {616, 541}, {425, 596, 382}]

import pandas as pd

for cluster in clusters:
    count = 0
    gbfs_cluster = None
    for station in cluster:
        gbfs_station= pd.read_csv(f"Data/gbfs_station_hour/Config 3/station_{int(station)}.csv", index_col="datetime", parse_dates=True)
        try:
            gbfs_cluster["bike_availability"] = gbfs_cluster["bike_availability"] + gbfs_station["bike_availability"]
            count += 1
        
        except:
            gbfs_cluster = gbfs_station
            count += 1
    gbfs_cluster["bike_availability"] = gbfs_cluster["bike_availability"]/count
    gbfs_cluster.to_csv(f"Data/gbfs_station_hour/Config 3/station_{clusters.index(cluster)+1}.csv")
    print(f"Cluster {clusters.index(cluster)+1} done")