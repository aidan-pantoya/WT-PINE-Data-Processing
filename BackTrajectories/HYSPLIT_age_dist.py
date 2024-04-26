import csv
import geopandas as gpd
from shapely.geometry import shape, Point, Polygon
import requests
import json
from shapely.validation import explain_validity
import numpy
import cv2
import plotly.graph_objs as go
import math
import os
import glob
import pandas as pd
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union
import sys
import time

pltnum = -72

site = 'NSA'

# metfile = 'GDAS1'
metfile = 'GFS'

directory = f"D:/backtrajectories/{metfile}/NSA/processed"

files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]

run_selected_days = False

runH = False
runL = False

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def distance_with_altitude(lat1, lon1, alt1, lat2, lon2, alt2):
    base_distance = haversine(lat1, lon1, lat2, lon2)
    alt_diff_km = abs(alt2 - alt1) / 1000.0
    total_distance = math.sqrt(base_distance**2 + alt_diff_km**2)
    return total_distance


if site == 'NSA':
    timeperiods = []
    starttime = pd.to_datetime('2021-12-01',format='%Y-%m-%d') # one year
    stoptime = pd.to_datetime('2022-12-01',format='%Y-%m-%d')
    time1 = '2021-12-01'
    time2 =  '2022-12-01'
    
    rundaysH = pd.read_csv(f"D:/Apr_3_2024/HighLowINP/6/ExINP_{site}_6H_{time1}-{time2}_fig4_HIGHINP.csv")
    rundaysH = rundaysH['time_reference']

    rundaysL = pd.read_csv(f"D:/Apr_3_2024/HighLowINP/6/ExINP_{site}_6H_{time1}-{time2}_fig4_LOWINP.csv")
    rundaysL = rundaysL['time_reference']

    timeperiods.append([starttime,stoptime,time1,time2])

    starttime = pd.to_datetime('2021-12-01',format='%Y-%m-%d') # winter
    stoptime = pd.to_datetime('2022-03-01',format='%Y-%m-%d')
    time1 = '2021-12-01'
    time2 =  '2022-03-01'
    timeperiods.append([starttime,stoptime,time1,time2])
    starttime = pd.to_datetime('2022-03-01',format='%Y-%m-%d') # spring
    stoptime = pd.to_datetime('2022-06-01',format='%Y-%m-%d')
    time1 = '2022-03-01'
    time2 =  '2022-06-01'
    timeperiods.append([starttime,stoptime,time1,time2])
    starttime = pd.to_datetime('2022-06-01',format='%Y-%m-%d') # summer
    stoptime = pd.to_datetime('2022-09-01',format='%Y-%m-%d')
    time1 = '2022-06-01'
    time2 =  '2022-09-01'
    timeperiods.append([starttime,stoptime,time1,time2])
    starttime = pd.to_datetime('2022-09-01',format='%Y-%m-%d') # fall
    stoptime = pd.to_datetime('2022-12-01',format='%Y-%m-%d')
    time1 = '2022-09-01'
    time2 =  '2022-12-01'
    timeperiods.append([starttime,stoptime,time1,time2])
    for start_date,end_date,time1,time2 in timeperiods:
        rancount = 0
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        
        if run_selected_days:
            if runH:
                outputfile= f"D:/Apr_3_2024/NSA_age_dist_{metfile}_{time1}-{time2}_HIGHINP.csv"
            elif runL:
                outputfile= f"D:/Apr_3_2024/NSA_age_dist_{metfile}_{time1}-{time2}_LOWINP.csv"
        else:
            outputfile= f"D:/Apr_3_2024/NSA_age_dist_{metfile}_{time1}-{time2}.csv"

        EndFile = [['MonthDayYearHr','Age (hr)','Distance (km)']]
        age = 0
        dist = 0
        aget = 0
        distt = 0

        endAll = 0

        randays = []

        for stupidFile in files:
            tmp_land1 = 0
            tmp_water1 = 0
            tmp_ice1 = 0
            regione = 'Bad'
            lastpntarray = []
            if endAll == 0:
                filepathr = stupidFile
                print(filepathr)
                with open(filepathr, 'r') as infile: 
                    lines = infile.readlines()
                    lines = lines[1:]
                    section = 0
                    x = -1
                    runnum = 0
                    for line in lines: 
                        values = line.split(",")  # Splitting based on comma for CSV
                        sec = int(values[0])
                        year = int(values[2])
                        month = int(values[3])
                        day = int(values[4])
                        hr = int(values[5])
                        pntfake = float(values[8])  # point (starts at 0 and goes to -96)
                        lat = float(values[9])  # latitude - converting string to float for classify_region function
                        lgt = float(values[10])  # longitude - converting string to float
                        altd = float(values[11])
                        rain = float(values[13])

                        if runnum != sec:
                            x+=1
                            lastpntarray.append(pltnum)
                            runnum +=1
                        if pntfake == 0:
                            pnt = 0
                        else:
                            pnt -=1
                        if pnt >= pltnum:
                            if pnt == 0:
                                rainsum = 0
                            rainsum += rain
                            if rainsum < 7:
                                lastpntarray[x] = pnt

                    x = -1
                    runnum = 0
                    pnt = 0
                    for line in lines: 
                        values = line.split(",")  # Splitting based on comma for CSV
                        sec = int(values[0])
                        year = int(values[2])
                        month = int(values[3])
                        day = int(values[4])
                        hr = int(values[5])
                        pntfake = float(values[8])  # point (starts at 0 and goes to -96)
                        lat = float(values[9])  # latitude - converting string to float for classify_region function
                        lgt = float(values[10])  # longitude - converting string to float
                        altd = float(values[11])
                        rain = float(values[13])
                        
                        if runnum != sec:
                            x+=1
                            runnum +=1
                        if pntfake == 0:
                            keepgoing = 0
                            pnt = 0
                            Travel_dist = 0
                            lat2,lgt2,altd2 = lat,lgt,altd
                        else:
                            pnt -=1

                        if pnt == -1:
                            keepgoing = 0
                            savedDay = day
                            savedMonth = month
                            savedHr = hr
                            savedYear = year
                            savedDatetime = pd.to_datetime(f'{savedDay}-{savedMonth}-{savedYear}',format='%d-%m-%y').date()
                            if run_selected_days:
                                if savedDatetime >= start_date and savedDatetime < end_date:

                                    for runday in rundaysH:
                                        runday = pd.to_datetime(runday).date()
                                        if savedDatetime == runday:
                                            keepgoing = 1

                                    if keepgoing == 0:
                                        for runday in rundaysL:
                                            runday = pd.to_datetime(runday).date()
                                            if savedDatetime == runday:
                                                keepgoing = 1
                                    elif runL:
                                        keepgoing = 0

                            elif savedDatetime >= start_date and savedDatetime < end_date:
                                keepgoing = 1


                        if keepgoing == 1:
                            if pnt == -1:
                                print(f'running [{savedDatetime}] is between [{start_date}] and [{end_date}]')
                            pltnumsp = lastpntarray[x]
                            if pnt >= pltnumsp and pnt != 0:
                                
                                td = distance_with_altitude(lat, lgt, altd, lat2, lgt2, altd2)
                                Travel_dist += td
                                lat2,lgt2,altd2 = lat,lgt,altd

                            if pnt == pltnumsp:
                                alreadyAdded = 0
                                for rd in randays:
                                    if savedDay == rd[0] and savedMonth==rd[1] and savedHr==rd[2] and savedYear==rd[3]:
                                        alreadyAdded = 1
                                        break
                                if alreadyAdded == 0:
                                    randays.append((savedDay,savedMonth,savedHr,savedYear))

                                    EndFile.append((str(savedMonth)+'/'+str(savedDay)+'/'+str(year)+' '+str(savedHr-5).zfill(2)+":00",pltnumsp,Travel_dist))
                                    print(f'Age: {pltnumsp}, Dist: {Travel_dist}')
                                    aget+=pltnumsp
                                    distt += Travel_dist
                                   
                                    rancount +=1

        EndFile.append(('Total For All:',aget,distt))
        EndFile.append(('Percentage For All:',aget/rancount,distt/rancount))

        with open(outputfile, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(EndFile)