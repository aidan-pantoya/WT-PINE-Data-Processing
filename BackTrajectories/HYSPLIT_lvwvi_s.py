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

run_selected_days = True

runH = True
runL = False

def preprocess_and_correct_geometries(df):
    df['geometry'] = df['geometry'].apply(lambda geom: geom.buffer(0) if not geom.is_valid else geom)
    return df

regions = preprocess_and_correct_geometries(regions)

def find_and_draw_sea_ice_boundaries(image_path):
    img = cv2.imread(image_path)

    img = img[0:int(img.shape[0]/(1.012)), :]
    img = img[int(img.shape[0]/(15)):img.shape[0], :]

    img = img[:,0:int(img.shape[1]/(1.28))]
    img = img[:,int(img.shape[1]/35):img.shape[1]]

    img = cv2.blur(img,(3,3))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_height, img_width = img.shape[:2]
    center_x, center_y = img_width / 2, img_height / 2
    max_radius = min(center_x, center_y)
    scale_factor = 0.41
    geo_boundaries = []
    for contour in contours:
        if cv2.contourArea(contour) < 5:
            continue
        cv2.drawContours(img, [contour], -1, (0, 255, 0), thickness=cv2.FILLED)
        geo_contour = []
        for point in contour:
            x, y = point[0]
            dx, dy = x - center_x, y - center_y
            radius = math.sqrt(dx**2 + dy**2)
            angle = math.atan2(dy, dx)
            lat = 90 - (radius / max_radius * 90 * scale_factor)
            lon = (angle / math.pi * 180) % 360
            lon = -lon
            lon +=44.8
            if lon > 180:
                lon -= 360

            lat = max(min(lat, 90), -90)
            geo_contour.append((lon, lat))
        geo_boundaries.append(geo_contour)
    # cv2.imshow('og', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return geo_boundaries

def plot_boundaries_on_map(boundaries):
    fig = go.Figure()
    for boundary in boundaries:
        lons, lats = zip(*boundary)
        fig.add_trace(go.Scattergeo(
            lon = lons,
            lat = lats,
            mode = 'lines',
            line = dict(width = 2, color = 'blue'),
        ))
    fig.update_layout(
        title = 'Sea Ice Boundaries Near North Pole',
        geo = dict(
            projection_type = 'orthographic',
            projection_rotation = dict(lon = 0, lat = 90, roll = 0),
            showland = True,
            landcolor = "LightGreen",
            showocean = True,
            oceancolor = "LightBlue"
        ),
    )
    fig.show()


def find_png_files(directory, pattern):
    search_pattern = os.path.join(directory, f'*{pattern}*.png')
    matching_files = glob.glob(search_pattern)

    return matching_files

def create_geometry_df(polygons):
    merged_polygon = unary_union(polygons)

    df = pd.DataFrame({'geometry': [merged_polygon]})
    return df


def extract_coordinates(geometry):
    if isinstance(geometry, MultiPolygon):
        return [list(polygon.exterior.coords) for polygon in geometry.geoms]
    elif isinstance(geometry, Polygon):
        return [list(geometry.exterior.coords)]
    else:
        raise TypeError("Geometry must be a Polygon or MultiPolygon")

def classify_landvwater(lat, lgt,regions,day,mnth,yr):
    point = Point(lgt, lat)

    for _, row in regions.iterrows():
        polygon = row['geometry']
        if not polygon.is_valid:
            polygon = polygon.buffer(0)  
        if point.within(polygon):
            return row['ADMIN']

    icefile = 'D:/SeaIceExtent'
    foundicefiles = find_png_files(icefile, str(yr).zfill(2)+str(mnth).zfill(2)+str(day).zfill(2))

    geo_boundaries = []
    for foundicefile in foundicefiles:
        boundaries = find_and_draw_sea_ice_boundaries(foundicefile)
        for coords in boundaries:
            df = create_geometry_df([Polygon(coords)])
            if df is not None:
                geo_boundaries.append(df)

    extracted_boundaries = []
    for df in geo_boundaries:
        for _, row in df.iterrows():
            coords_list = extract_coordinates(row['geometry'])
            for coords in coords_list:
                extracted_boundaries.append(coords)

    # plot_boundaries_on_map(extracted_boundaries)
    # time.sleep(1)

    if not geo_boundaries:
        print(f'ice bad date: {str(yr).zfill(2)+str(mnth).zfill(2)+str(day).zfill(2)}')
        print("No valid geo boundaries were created.")
    else:
        for df in geo_boundaries:
            for _, row in df.iterrows():
                if point.within(row['geometry']):
                    return 'Ice'
            else:
                continue

    return 'Ocean'

def classify_region(lat, lgt,regions): # Function to classify the region of a point
    point = Point(lgt, lat) 
    Result = 'Ocean'

    for _, row in regions.iterrows():
        polygon = row['geometry']

        if not polygon.is_valid:
            print(f"Invalid geometry detected: {explain_validity(polygon)}")
            polygon = polygon.buffer(0)  

        if point.within(polygon):
            Result = row['ADMIN']
            break

    if Result == 'Ocean':
        Result = check_marginal_arctic_seas(lat,lgt) # if ocean, check if in a marginal arctic sea.
        if Result != 'Ocean':
            return Result

    if lat > 66:
        if Result == 'Ocean':
            return 'Arctic Ocean'
        # elif Result == 'Canada' or Result == 'United States of America':
            # return 'Arctic Circle'

    if Result == 'Ocean':
        if lat > 54 and ((lgt > -23 and lgt < 0) or (lgt >= 0 and lgt < 24)):
            return 'Norwegian Sea'

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

    if Result == 'Russia' or Result == 'China' or Result == 'Japan' or Result == 'North Korea' or Result == 'South Korea':
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
    # Amundsen Gulf   68.5°N to 70.5°N    128.5°W to 136.5°W gg
    # Baffin Bay  66.5°N to 78.5°N    55.5°W to 80.5°W gg
    # Barents Sea 70.5°N to 81.5°N    20.5°E to 65.5°E gg
    # Beaufort Sea    68.5°N to 76.5°N    126.5°W to 141.5°W gg
    # Chukchi Sea 64.5°N to 72.5°N    160.5°W to 180° gg
    # Davis Strait    60.5°N to 70.5°N    45.5°W to 62.5°W gg
    # East Siberian Sea   67.5°N to 77.5°N    140.5°E to 180° gg
    # Greenland Sea   68.5°N to 82.5°N    10.5°W to 20.5°E gg
    # Hudson Bay  51.5°N to 63.5°N    75.5°W to 96.5°W gg
    # Hudson Strait   60.5°N to 63.5°N    68.5°W to 78.5°W gg
    # Labrador Sea    53.5°N to 63.5°N    45.5°W to 60.5°W gg
    # Laptev Sea  70.5°N to 80.5°N    90.5°E to 140.5°E gg
    # Kara Sea    67.5°N to 81.5°N    60.5°E to 90.5°E gg
    # from worldatlas.com

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
        
        if run_selected_days:
            if runH:
                outputfile= f"D:/Apr_3_2024/NSA_lvwvi_s_{metfile}_{time1}-{time2}_HIGHINP.csv"
            elif runL:
                outputfile= f"D:/Apr_3_2024/NSA_lvwvi_s_{metfile}_{time1}-{time2}_LOWINP.csv"
        else:
            outputfile= f"D:/Apr_3_2024/NSA_lvwvi_s_{metfile}_{time1}-{time2}.csv"

        EndFile = [['MonthDayYearHr','Inlet Height Over Land %','Inlet Height Over Water %','Inlet Height Over Ice %','Inlet Height Source']]
        water = 0
        ice = 0
        land = 0
        water1 = 0
        ice1 = 0
        land1 = 0
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
                            if pnt >= pltnumsp:
                                if pnt < 0 and -pnt % 6 == 0: # checking every 6th hour, excluding the end point (NSA site)
                                    region = classify_landvwater(lat, lgt, regions,day,month,year)    
                                    print(region)
                                    if region == 'Ocean':
                                        water += 1
                                        tmp_water1 +=1
                                        water1 +=1
                                    elif region == 'Ice':
                                        ice +=1
                                        tmp_ice1 +=1
                                        ice1 +=1
                                    else:
                                        land += 1
                                        tmp_land1 += 1
                                        land1 +=1

                            if pnt == pltnumsp:
                                alreadyAdded = 0
                                for rd in randays:
                                    if savedDay == rd[0] and savedMonth==rd[1] and savedHr==rd[2] and savedYear==rd[3]:
                                        alreadyAdded = 1
                                        break
                                if alreadyAdded == 0:
                                    randays.append((savedDay,savedMonth,savedHr,savedYear))
                                    regione = classify_region(lat, lgt,regions) 
                                    print(regione)
                                    region1 = regione
                                    if 'Not sure' in region1:
                                        print("Not in a section???")
                                        print("Check: "+f'{stupidFile}') 
                                        sys.exit()

                                    if (tmp_land1+tmp_water1+tmp_ice1) > 0:
                                        LandPrct1 = round(tmp_land1/(tmp_land1+tmp_water1+tmp_ice1) * 100,3)
                                        WaterPrct1 = round(tmp_water1/(tmp_land1+tmp_water1+tmp_ice1) * 100,3)
                                        IcePrct1 = round(tmp_ice1/(tmp_land1+tmp_water1+tmp_ice1) * 100,3)
                                    else:
                                        LandPrct1 = '7mm rain before 6hr'
                                        WaterPrct1 = '7mm rain before 6hr'
                                        IcePrct1 = '7mm rain before 6hr'

                                    print(f"Over Land: {LandPrct1} %")
                                    print(f"Over Water: {WaterPrct1} %")
                                    print(f"Over Ice: {IcePrct1} %")

                                    EndFile.append((str(savedMonth)+'/'+str(savedDay)+'/'+str(year)+' '+str(savedHr-5).zfill(2)+":00",LandPrct1,WaterPrct1,IcePrct1,region1))
                                   
                                    tmp_land1 = 0
                                    tmp_water1 = 0
                                    tmp_ice1 = 0
                                    regione = 'Bad'


        landt1 = round(land1/(land1+water1+ice1) * 100,3)
        watert1 = round(water1/(land1+water1+ice1) * 100,3)
        icet1 = round(ice1/(land1+water1+ice1) * 100,3)


        EndFile.append(('Total Percentage For Each:',landt1,watert1,icet1))

        landt = round(land/(land+water+ice) * 100,3)
        watert = round(water/(land+water+ice) * 100,3)
        icet = round(ice/(land+water+ice) * 100,3)
                            
        print('Total Land: '+str(landt))
        print('Total Water: '+str(watert))
        print('Total Ice: '+str(icet))

        EndFile.append(('Total Percentage For All:',landt,watert,icet))

        with open(outputfile, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(EndFile)
            print("Land Water Ice Percentage Complete!")