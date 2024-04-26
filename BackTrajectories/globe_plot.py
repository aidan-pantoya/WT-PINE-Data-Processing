import plotly.graph_objs as go
import geopandas as gpd
import glob
import pandas as pd
import re
from datetime import datetime
import time
import numpy as np
from collections import defaultdict
import csv
from shapely.geometry import shape, Point, Polygon
import requests
import json
from shapely.validation import explain_validity
import cv2
import math
import os
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union


site = 'NSA'

# directory = "D:/backtrajectories/GFS/NSA/processed"

directory = "D:/backtrajectories/GDAS1/NSA/processed"

# testphrase = '05Dec21'

pltnum = -72


if site == 'NSA':
    timeperiods = []
    starttime = pd.to_datetime('2021-12-01',format='%Y-%m-%d') # one year
    stoptime = pd.to_datetime('2022-12-01',format='%Y-%m-%d')
    time1 = '2021-12-01'
    time2 =  '2022-12-01'

    runHs = pd.read_csv(f"D:/Apr_3_2024/HighLowINP/6/ExINP_{site}_6H_{time1}-{time2}_fig4_HIGHINP.csv")
    runLs = pd.read_csv(f"D:/Apr_3_2024/HighLowINP/6/ExINP_{site}_6H_{time1}-{time2}_fig4_LOWINP.csv")
    runHs = runHs['time_reference']
    runLs = runLs['time_reference']

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

        # runHs = pd.read_csv(f"D:/Apr_3_2024/HighLowINP/6/ExINP_{site}_6H_{time1}-{time2}_fig4_HIGHINP.csv")
        # runLs = pd.read_csv(f"D:/Apr_3_2024/HighLowINP/6/ExINP_{site}_6H_{time1}-{time2}_fig4_LOWINP.csv")
        # runHs = runHs['time_reference']
        # runLs = runLs['time_reference']

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

        files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]

        randays = []

        # Load your world countries data
        wc = gpd.read_file("D:/backtrajectories/countries.geojson")  # Replace with your actual file path

        # Convert GeoDataFrame to a format Plotly understands
        wc['lon'] = wc.geometry.centroid.x
        wc['lat'] = wc.geometry.centroid.y

        # Albsa_df = pd.read_excel("E:/HySplit/ALBSA_SORT.xlsx")

        def parse_custom_time_format(custom_time):
            match = re.match(r'(\d{2})([A-Za-z]+)(\d{2})_(\d{2})', custom_time)
            if not match:
                raise ValueError("Invalid format")
            day, month, year, hour = match.groups()
            formatted_time = f'{day} {month} {year} {hour}'
            return datetime.strptime(formatted_time, '%d %b %y %H')

        def column_values(df,checkDate):
            for value,rett in zip(df.iloc[:, 0],df.iloc[:, 1]):
                if checkDate == value:
                    return rett
            return 7777777      

        def preprocess_and_correct_geometries(df):
            df['geometry'] = df['geometry'].apply(lambda geom: geom.buffer(0) if not geom.is_valid else geom)
            return df

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


        fig = go.Figure(data=go.Scattergeo(
            lon = wc['lon'],
            lat = wc['lat'],
            mode = 'markers',
            marker = dict(
                size = 1,
                color = 'blue',
            )
        ))

        EARTH_RADIUS = 6371  # in km
        DEGREE_TO_KM = math.pi * EARTH_RADIUS / 180  # km per degree

        def km_to_deg_longitude(km, latitude):
            return km / (math.cos(math.radians(latitude)) * DEGREE_TO_KM)

        if site == 'HOU':
            latitude = 18
            start_longitude = -87
        elif site == 'NSA':
            latitude = 40
            start_longitude = -150
        else:
            latitude = 10
            start_longitude = 10
        span_degrees = km_to_deg_longitude(500, latitude)

        end_longitude = start_longitude + span_degrees

        fig.add_trace(go.Scattergeo(
            lon = [start_longitude, end_longitude],
            lat = [latitude, latitude],
            mode = 'lines',
            line = dict(width = 4, color = 'black'),
            name = '500 km scale bar'
        ))

        fig.add_trace(go.Scattergeo(
            lat = lt1,
            lon = ln1,
            mode = 'markers',
            marker = dict(
                size = 25, 
                color = 'black',
                symbol = 'star' 
            ),
            showlegend=False
        ))

        fig.add_trace(go.Scattergeo(
            lat = lt1,
            lon = ln1,
            name = 'M1 Site',
            mode = 'markers',
            marker = dict(
                size = 20, 
                color = 'yellow',
                symbol = 'star' 
            )
        ))

        for stupidFile in files:
            runnum = 0
            lastpntarray = []
            with open(stupidFile, 'r') as infile: 
                lines = infile.readlines()
                lines = lines[1:]
                # AlbsaVal = column_values(Albsa_df, checkDate)
                if True:
                    section_points = defaultdict(list)
                    x = -1
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
                    colorandlabel=[]
                    usedlabel = []
                    noaddlabel = False
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
                        if runnum != sec:
                            x+=1
                            runnum +=1
                        if pntfake == 0:
                            keepgoing = 0
                            pnt = 0
                        else:
                            pnt -=1
                        if sec != runnum:
                            runnum = sec

                        if pnt == -1:
                            keepgoing = 0
                            color = 'white'
                            label = '...'
                            savedDay = day
                            savedMonth = month
                            savedHr = hr
                            savedYear = year
                            savedDatetime = pd.to_datetime(f'{savedDay}-{savedMonth}-{savedYear}',format='%d-%m-%y').date()
                            if savedDatetime >= start_date and savedDatetime < end_date:
                                keepgoing = 1
                                for runH in runHs:
                                    runH = pd.to_datetime(runH).date()
                                    if runH == savedDatetime:
                                        color = 'cyan'
                                        break
                                if color == 'white':
                                    for runL in runLs:
                                        runL = pd.to_datetime(runL).date()
                                        if runL == savedDatetime:
                                            color = 'red'
                                            break

                        if keepgoing == 1:
                            pltnumsp = lastpntarray[x]
                            if pnt >= lastpntarray[x]:
                                if pnt == lastpntarray[x]:
                                    alreadyAdded = 0
                                    for rd in randays:
                                        if savedDay == rd[0] and savedMonth==rd[1] and savedHr==rd[2]:
                                            alreadyAdded = 1
                                            break
                                    if alreadyAdded == 0:
                                        randays.append((savedDay,savedMonth,savedHr))
                                        fig.add_trace(go.Scattergeo(
                                            lon = [lgt],
                                            lat = [lat],
                                            name = f'MM/DD: {label}',
                                            mode = 'markers',
                                            marker = dict(
                                                size = 5,  # Adjust size as needed
                                                color = [color],  # Adjust color as needed
                                            ),
                                            showlegend = False
                                        ))
                                        
                                if True:#pnt < pltnumsp/1.1:
                                    section_points[sec].append((lgt, lat))
                                    colorandlabel.append((sec,color,label))


                    for (sec, points) in section_points.items():
                        for xxx in colorandlabel:
                            secx,color,lablel = xxx
                            if secx == sec:
                                break
                        # color = 'cyan'
                        lons, lats = zip(*points)
                        fig.add_trace(go.Scattergeo(
                            lon = lons,
                            lat = lats,
                            name = f'MM/DD: {label}',
                            mode = 'lines',
                            line = dict(color=str(color), width=0.5),
                            showlegend = False
                            # marker = dict(size=1, color=color)
                        ))


        # icefile = 'E:/HySplit/iceimages'

        # foundicefiles = find_png_files(icefile,testphrase)

        # geo_boundaries = []
        # for foundicefile in foundicefiles:
        #     boundaries = find_and_draw_sea_ice_boundaries(foundicefile)
        #     for coords in boundaries:
        #         df = create_geometry_df([Polygon(coords)])
        #         if df is not None:
        #             geo_boundaries.append(df)

        # extracted_boundaries = []
        # for df in geo_boundaries:
        #     for _, row in df.iterrows():
        #         coords_list = extract_coordinates(row['geometry'])
        #         for coords in coords_list:
        #             extracted_boundaries.append(coords)

        # for boundary in extracted_boundaries:
        #     lons, lats = zip(*boundary)
        #     fig.add_trace(go.Scattergeo(
        #         lon = lons,
        #         lat = lats,
        #         mode = 'lines',
        #         line = dict(width = 2, color = 'blue'),
        #     ))
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

        fig.update_layout(
            title = 'Interactive 3D Globe',
            geo = dict(
                projection_type = 'orthographic',
                showland = True,
                landcolor = "rgb(50, 50, 50)",
                countrycolor = "rgb(50, 50, 50)",
            ),
        )
        # for runday in rundays:
        #     testmonth = runday[0]
        #     testday = runday[1]
        #     color = runday[2]
        #     label = str(testmonth)+'/'+str(testday)
        #     fig.add_trace(go.Scattergeo(
        #         lon = [-88],
        #         lat = [-88],
        #         name = f'MM/DD: {label}',
        #         mode = 'markers',
        #         marker = dict(
        #             size = 5,  # Adjust size as needed
        #             color = [color],  # Adjust color as needed
        #         )
        #     ))


        # fig.add_shape(type="line",
        #               x0=0.75, y0=0.05, x1=0.85, y1=0.05,
        #               line=dict(color="Black", width=2))

        fig.add_annotation(x=0.8, y=0.055, text="500 km",
                           showarrow=False, textangle=0)


        fig.show()