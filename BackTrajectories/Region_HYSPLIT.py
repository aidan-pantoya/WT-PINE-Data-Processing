import csv
import geopandas as gpd
from shapely.geometry import Point
import requests
import os
import sys
import pandas as pd

pltnum = -72

site = 'NSA'

if site == 'ENA':
    lt1 = [39.5297]
    ln1 = [-28.1325]
elif site == 'SGP':
    lt1 = [36.3626]
    ln1 = [-97.2915]
elif site == 'NSA':
    lt1 = [71.323]
    ln1 = [-156.6114]
elif site == 'HOUM1':
    lt1 = [29.67]
    ln1 = [-95.059]


metfile = 'GDAS1'
# metfile = 'GFS'

directory = f"D:/backtrajectories/{metfile}/NSA/processed"

files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]

regions = gpd.read_file("E:/HySplit/countries.geojson") # path to the countries geoJSON file

run_selected_days = False

runH = False
runL = True

def preprocess_and_correct_geometries(df):
    df['geometry'] = df['geometry'].apply(lambda geom: geom.buffer(0) if not geom.is_valid else geom)
    return df

regions = preprocess_and_correct_geometries(regions)

def classify_region(lat, lgt,regions): # Function to classify the region of a point
    point = Point(lgt, lat) 
    Result = 'Ocean'

    for _, row in regions.iterrows():
        polygon = row['geometry']

        # Check if the geometry is valid
        if not polygon.is_valid:
            print(f"Invalid geometry detected: {explain_validity(polygon)}")
            polygon = polygon.buffer(0)  # Attempt to fix the geometry

        if point.within(polygon):
            Result = row['ADMIN']
            break

    if Result == 'Ocean':
        Result = check_marginal_arctic_seas(lat,lgt) # if over water, checks if in a marginal sea
        if Result != 'Ocean':
            return Result

    if lat > 66:
        if Result == 'Ocean':
            return 'Arctic Ocean'
        # elif Result == 'United States of America' or Result == 'Canada': # if we want to include Arctic Circle, we can
            # return 'Arctic Circle'
    if Result == 'Ocean':
        if lat > 54 and ((lgt > -23 and lgt < 0) or (lgt >= 0 and lgt < 24)):
            return 'Norwegian Sea'
    if Result == 'Russia':
        return 'Eurasia'
    if Result == 'Canada' or Result == 'United States of America' or Result == 'Mexico' or Result == 'Cuba':
        return 'North America'
    if Result == 'Iceland' or Result == 'Greenland':
        return 'Greenland & Iceland'

    if Result == 'Ocean':
        if lgt >-100 and lgt < -80 and lat<31 and lat >17:
            return 'Gulf of Mexico'
        elif (lgt < -97 or lgt > 120) and lat >16:
            return 'Pacific Ocean'
        elif lgt < -75 and lat <16:
            return 'Pacific Ocean'
        elif lgt < -7 and lgt > -79.999:
            return 'Atlantic Ocean'

    if Result == 'China' or Result == 'Japan' or Result == 'North Korea' or Result == 'South Korea':
        return 'Eurasia'
    if Result == 'Algeria' or Result == 'Niger' or Result == 'Libya' or Result == 'Mauritania' or Result == 'Western Sahara' or Result == 'Morocco' or Result == 'Mali' or Result == 'Tunisia':
        return 'Western Africa'

    if Result == 'Spain' or Result == 'Portugal' or Result == 'France' or Result == 'Ireland' or Result == 'Poland' or Result == 'Italy' or Result == 'Belgium'\
                 or Result == 'Germany' or Result == 'United Kingdom' or Result == 'Belgium' or Result == 'Netherlands' or Result == 'Norway' or Result == 'Austria' \
                    or Result == 'Hungary' or Result == 'Romania' or Result == 'Serbia' or Result == 'Czechia':
        return 'Europe'

    print('Did not find for: '+str(Result))
    return 'Not sure: '+str(lat)+', '+str(lgt)


def check_marginal_arctic_seas(lat,lgt): 
    # Amundsen Gulf   68.5°N to 70.5°N    128.5°W to 136.5°W 
    # Baffin Bay  66.5°N to 78.5°N    55.5°W to 80.5°W 
    # Barents Sea 70.5°N to 81.5°N    20.5°E to 65.5°E 
    # Beaufort Sea    68.5°N to 76.5°N    126.5°W to 141.5°W 
    # Chukchi Sea 64.5°N to 72.5°N    160.5°W to 180° 
    # Davis Strait    60.5°N to 70.5°N    45.5°W to 62.5°W 
    # East Siberian Sea   67.5°N to 77.5°N    140.5°E to 180° 
    # Greenland Sea   68.5°N to 82.5°N    10.5°W to 20.5°E 
    # Hudson Bay  51.5°N to 63.5°N    75.5°W to 96.5°W 
    # Hudson Strait   60.5°N to 63.5°N    68.5°W to 78.5°W 
    # Labrador Sea    53.5°N to 63.5°N    45.5°W to 60.5°W 
    # Laptev Sea  70.5°N to 80.5°N    90.5°E to 140.5°E 
    # Kara Sea    67.5°N to 81.5°N    60.5°E to 90.5°E 
    # from https://www.worldatlas.com/articles/the-marginal-seas-of-the-arctic-ocean.html

    # Smith Bay     70.5 N to 71 N    -154.5 to -154

    seas = [(68.5,70.5,-136.8,-128.5),(66.5,78.5,-80.5,-55.5),(70.5,81.5,20.5,65.5),(68.5,76.5,-141.5,-126.5),(64.5,72.5,-180,-160.5),(60.5,70.5,-62.5,-45.5),\
    (67.5,77.5,140.5,180),(68.5,82.5,10.5,20.5),(51.5,66.0,-96.5,-75.5),(70.5,71,-154.5,-154),(60.5,63.5,-78.5,-68.5),(53.5,63.5,-60.5,-45.5),(70.5,80.5,90.5,140.5),(67.5,81.5,60.5,90.5)]
    for x in seas:
        if x[0] <= lat and x[1]>=lat and x[2]<=lgt and x[3]>=lgt:
            return 'Marginal Arctic Ocean'
    return 'Ocean'



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
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        print(f'start: {start_date}, end: {end_date}')

        if run_selected_days:
            if runH:
                outputfile= f"D:/Apr_3_2024/NSA_region_{metfile}_{time1}-{time2}_HIGHINP.csv"
            elif runL:
                outputfile= f"D:/Apr_3_2024/NSA_region_{metfile}_{time1}-{time2}_LOWINP.csv"
        else:
            outputfile= f"D:/Apr_3_2024/NSA_region_{metfile}_{time1}-{time2}.csv"

        # FoundRegions = ['arctic circle','arctic Ocean','Atlantic Ocean','Europe','Greenland & Iceland','Gulf of Mexico','Latin America','Marginal arctic Ocean','North America','Norwegian Sea','Pacific Ocean','Russia','Western Africa']
        EndFile = [['','Inlet Height %','Inlet Height Total']]

        arctic_circle_1 = 0 # Counters for each region
        arctic_ocean_1 = 0
        atlantic_ocean_1 = 0
        europe_1 = 0
        greenland_and_iceland_1 = 0
        gulf_of_mexico_1 = 0 
        latin_america_1 = 0 
        marginal_arctic_ocean_1 = 0
        north_america_1 = 0
        norwegian_sea_1 = 0
        pacific_ocean_1 = 0 
        russia_1 = 0
        western_africa_1 = 0
        total1 = 0

        randays = []

        for stupidFile in files:  
            filepathr = stupidFile
            print(filepathr)
            x=-1
            runnum = 0
            keepgoing = 0
            lastpntarray = []
            with open(filepathr, 'r') as infile:
                lines = infile.readlines()
                lines = lines[1:]
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
                pnt = 0
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
                            runnum +=1
                    if pntfake == 0:
                        keepgoing = 0
                        pnt = 0
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
                        if pnt == pltnumsp:  
                            alreadyAdded = 0
                            for rd in randays:
                                if savedDay == rd[0] and savedMonth==rd[1] and savedHr==rd[2] and savedYear==rd[3]:
                                    alreadyAdded = 1
                                    break
                            if alreadyAdded == 0:
                                randays.append((savedDay,savedMonth,savedHr,savedYear))

                                region = classify_region(lat, lgt,regions) 
                                print(region)
                                if region == 'Arctic Circle': # Arctic Circle is not being included, not can easily be
                                    arctic_circle_1 +=1
                                elif region =='Arctic Ocean':
                                    arctic_ocean_1 +=1
                                elif region == 'Atlantic Ocean':
                                    atlantic_ocean_1 +=1
                                elif region =='Europe':
                                    europe_1+=1
                                elif region =='Greenland & Iceland':
                                    greenland_and_iceland_1+=1
                                elif region =='Gulf of Mexico':
                                    gulf_of_mexico_1 += 1
                                elif region =='Latin America':
                                    latin_america_1 +=1
                                elif region == 'Marginal Arctic Ocean':
                                    marginal_arctic_ocean_1 +=1
                                elif region =='North America':
                                    north_america_1 +=1
                                elif region == 'Norwegian Sea':
                                    norwegian_sea_1 +=1
                                elif region == 'Pacific Ocean':
                                    pacific_ocean_1 +=1
                                elif region == 'Eurasia':
                                    russia_1 += 1
                                elif region == 'Western Africa':
                                    western_africa_1 += 1
                                else:
                                    print('Did not find: '+str(region))
                                    print("Check: "+str(filepathr))
                                    sys.exit()
                                total1 += 1


        arctic_circle_tmp1 = round(arctic_circle_1/(total1) * 100,3)
        arctic_ocean_tmp1 = round(arctic_ocean_1/(total1) * 100,3)
        atlantic_ocean_tmp1 = round(atlantic_ocean_1/(total1) * 100,3)
        europe_tmp1 = round(europe_1/(total1) * 100,3)
        greenland_and_iceland_tmp1 = round(greenland_and_iceland_1/(total1) * 100,3)
        gulf_of_mexico_tmp1 = round(gulf_of_mexico_1/(total1) * 100,3) 
        latin_america_tmp1 = round(latin_america_1/(total1) * 100,3) 
        marginal_arctic_ocean_tmp1 = round(marginal_arctic_ocean_1/(total1) * 100,3)
        north_america_tmp1 = round(north_america_1/(total1) * 100,3)
        norwegian_sea_tmp1 = round(norwegian_sea_1/(total1) * 100,3)
        pacific_ocean_tmp1 = round(pacific_ocean_1/(total1) * 100,3) 
        russia_tmp1 = round(russia_1/(total1) * 100,3)
        western_africa_tmp1 = round(western_africa_1/(total1) * 100,3)
        tpct1 = arctic_circle_tmp1+arctic_ocean_tmp1+atlantic_ocean_tmp1+europe_tmp1+greenland_and_iceland_tmp1+\
            gulf_of_mexico_tmp1+latin_america_tmp1+marginal_arctic_ocean_tmp1+norwegian_sea_tmp1+north_america_tmp1+pacific_ocean_tmp1+\
            russia_tmp1+western_africa_tmp1

        # EndFile.append(('Arctic circle',arctic_circle_tmp1,arctic_circle_tmp2,arctic_circle_tmp3,arctic_circle_1,arctic_circle_2,arctic_circle_3)) # took out Arctic circle
        EndFile.append(('Arctic Ocean',arctic_ocean_tmp1,arctic_ocean_1))
        EndFile.append(('Atlantic Ocean',atlantic_ocean_tmp1,atlantic_ocean_1))
        EndFile.append(('Europe',europe_tmp1,europe_1))
        EndFile.append(('Greenland & Iceland',greenland_and_iceland_tmp1,greenland_and_iceland_1))
        EndFile.append(('Gulf of Mexico',gulf_of_mexico_tmp1,gulf_of_mexico_1))
        EndFile.append(('Latin America',latin_america_tmp1,latin_america_1))
        EndFile.append(('Marginal Arctic Ocean',marginal_arctic_ocean_tmp1,marginal_arctic_ocean_1))
        EndFile.append(('North America',north_america_tmp1,north_america_1))
        EndFile.append(('Norwegian Sea',norwegian_sea_tmp1,norwegian_sea_1))
        EndFile.append(('Pacific Ocean',pacific_ocean_tmp1,pacific_ocean_1))
        EndFile.append(('Eurasia',russia_tmp1,russia_1)) # says russia, but was transistioned to Eurasia
        EndFile.append(('Western Africa',western_africa_tmp1,western_africa_1))
        EndFile.append(('Totals:',tpct1,total1))

        with open(outputfile, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(EndFile)
            print("Regions!")

        print(EndFile)
        print('')
        print('totals (should all equal)')
        print(total1)
        print('Ran Times:')
        print(randays)