import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import os
from sklearn.metrics import r2_score
from numpy.polynomial.polynomial import Polynomial


def parse_date(date_str):
    for fmt in ('%d/%m/%Y %H:%M', '%d/%m/%y %H:%M'): 
        try:
            return pd.to_datetime(date_str, format=fmt).tz_localize('UTC')
        except ValueError:
            continue
    raise ValueError(f"Date format for {date_str} not recognized.")


sheetnames = ['GVB']
for sheetname in sheetnames:
    if sheetname == 'GVB':
        # starttime = pd.to_datetime('2023-03-15').tz_localize('UTC')
        # stoptime = pd.to_datetime('2023-04-11').tz_localize('UTC')
        # time1 = '2023-03-15'
        # time2 =  '2023-04-11'
        # starttime = pd.to_datetime('2023-03-15').tz_localize('UTC')
        # stoptime = pd.to_datetime('2023-04-01').tz_localize('UTC')
        # time1 = '2023-03-15'
        # time2 =  '2023-04-01'
        starttime = pd.to_datetime('2023-04-01').tz_localize('UTC')
        stoptime = pd.to_datetime('2023-04-11').tz_localize('UTC')
        time1 = '2023-04-01'
        time2 =  '2023-04-11'
    elif sheetname == 'NSA':
        starttime = pd.to_datetime('2021-10-21')
        stoptime = pd.to_datetime('2023-05-01')
    elif sheetname == 'SGP':
        starttime = pd.to_datetime('2019-10-01')
        stoptime = pd.to_datetime('2019-11-15')
    elif sheetname == 'ENA':
        starttime = pd.to_datetime('2020-10-01')
        stoptime = pd.to_datetime('2021-04-01')
    for hravg in [6,12,24,48,72]:
        if sheetname == 'SGP':
            if hravg == 6:
                rr,a,b,c,d=0.9967,23.46,0.041,12.9,2.1
            elif hravg == 12:
                rr,a,b,c,d=0.9863,27.333,0.035,12.6,0.5
            elif hravg == 24:
                rr,a,b,c,d=0.983,20.667,0.048,12.6,2.9
            elif hravg == 48:
                rr,a,b,c,d=0.9809,18,0.086,10.667,1.4
            elif hravg == 72:
                rr,a,b,c,d=0.9847,27.333,0.035,14.533,1.1
            labeler = f'B.'#                    INAS Density = exp({a} * exp(-exp({b} * (T + {c}))) + {d}), r = 0.86'

        elif sheetname == 'ENA':
            if hravg == 6:
                rr,a,b,c,d=0.9957,22,0.105,9.7,0.95
            elif hravg == 12:
                rr,a,b,c,d=0.9914,18,0.137,12.6,4.1
            elif hravg == 24:
                rr,a,b,c,d=0.9928,19.333,0.137,12.6,2.9
            elif hravg == 48:
                rr,a,b,c,d=0.9915,20.667,0.137,12.6,1.7
            elif hravg == 72:
                rr,a,b,c,d=0.9953,19.333,0.137,12.6,2.9
        elif sheetname == 'GVB' and starttime == pd.to_datetime('2023-03-15').tz_localize('UTC') and stoptime == pd.to_datetime('2023-04-11').tz_localize('UTC'):
            if hravg == 6:
                rr,a,b,c,d=0.9947,27.0,0.076,14.05,3.875
            elif hravg == 12:
                rr,a,b,c,d= 0.9893,27.0,0.067,14.05,4.775
            elif hravg == 24:
                rr,a,b,c,d=0.9614,29.0,0.076,15.5,2.975
            elif hravg == 48:
                rr,a,b,c,d=0.9958,24.0,0.181,16.95,2.075
            elif hravg == 72:
                rr,a,b,c,d=0.9963,23.0,0.105,14.05,4.775
        elif sheetname == 'GVB' and starttime == pd.to_datetime('2023-03-15').tz_localize('UTC') and stoptime == pd.to_datetime('2023-04-01').tz_localize('UTC'):
            if hravg == 6:
                rr,a,b,c,d= 0.9947,28.0,0.067,9.7,2.75
            elif hravg == 12:
                rr,a,b,c,d=0.995,29.0,0.076,9.7,0.95
            elif hravg == 24:
                rr,a,b,c,d=0.998,29.0,0.076,9.7,0.95
            elif hravg == 48:
                rr,a,b,c,d=0.9923,28.0,0.067,11.15,3.2
            elif hravg == 72:
                rr,a,b,c,d=0.9657,27.0,0.086,16.95,4.55
        elif sheetname == 'GVB' and starttime == pd.to_datetime('2023-04-01').tz_localize('UTC')and stoptime == pd.to_datetime('2023-04-11').tz_localize('UTC'):
            if hravg == 6:
                rr,a,b,c,d=0.9914,29.0,0.048,14.05,3.875
            elif hravg == 12:
                rr,a,b,c,d=0.9949,28.0,0.067,9.7,0.5
            elif hravg == 24:
                rr,a,b,c,d=0.9986,23.0,0.114,15.5,3.2
            elif hravg == 48:
                rr,a,b,c,d=0.9932,22.0,0.172,16.95,2.525
            elif hravg == 72:
                rr,a,b,c,d=0.9951,22.0,0.152,15.5,2.525
        else:
            a,b,c,d = 0,0,0,0

# --------------------------------
        csv_input_path = f"E:/ExINP_Total_Graphing/ExINP{sheetname}_WTAMU_L1MERGED_v3.csv"
        data = pd.read_csv(csv_input_path)
        maxtemp = -31

        if sheetname == 'ENA':
            SA_conc_df = pd.read_csv("E:/ExINP_Total_Graphing/enasurfaceareav2.csv")
            saname = 'S_totmax_m^2_L^-1'
            SA_conc_df.rename(columns={str(saname): 'merged_total_SA_conc'}, inplace=True)
            SA_conc_df['time'] = pd.to_datetime(SA_conc_df['time'])
            SA_conc_df = SA_conc_df[SA_conc_df['time'] >= pd.Timestamp('2020-10-01')]
            SA_conc_df = SA_conc_df[['time', 'merged_total_SA_conc']]
            SA_conc_df.set_index('time', inplace=True)
            if hravg > 6:
                SA_conc_df= SA_conc_df['merged_total_SA_conc'].resample(str(hravg)+'H',origin=pd.Timestamp('2020-10-01')).mean().reset_index()
            mintemp = -20

        elif sheetname == 'SGP':
            directory = 'E:/2_7_2024_SGP_DATA/245486/ascii-csv'
            SA_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]

            SA_dataframes = [pd.read_csv(file) for file in SA_files]
            mintemp = -15

            filtered_dataframes = []
            for df in SA_dataframes:
                df['time'] = pd.to_datetime(df['time'])
                df = df[df['time'] >= pd.Timestamp('2019-10-01')]
                filtered_df = df[df['qc_merged_total_SA_conc'] == 0]
                filtered_df = filtered_df[['time', 'merged_total_SA_conc']]
                filtered_df.set_index('time', inplace=True)
                filtered_dataframes.append(filtered_df)
            SA_conc_df = pd.concat(filtered_dataframes)
            if hravg > 6:
                SA_conc_df= SA_conc_df['merged_total_SA_conc'].resample(str(hravg)+'H',origin=pd.Timestamp('2019-10-01')).mean().reset_index()
            SA_conc_df['merged_total_SA_conc'] = SA_conc_df['merged_total_SA_conc'] * 1e-15

        elif sheetname == 'GVB':
            mintemp = -22
            maxtemp = -33
            origin = starttime
            SA_conc_df = pd.read_csv("E:/ExINP_Total_Graphing/gvbsurfacearea.csv")
            SA_conc_df.dropna()
            saname = 'SA_m^2_L^-1'
            SA_conc_df.rename(columns={str(saname): 'merged_total_SA_conc'}, inplace=True)
            SA_conc_df['time'] = SA_conc_df['time'].apply(parse_date)
            SA_conc_df = SA_conc_df[['time', 'merged_total_SA_conc']]
            SA_conc_df = SA_conc_df[~SA_conc_df['merged_total_SA_conc'].str.contains('VALUE', case=False, na=False)].copy()
            SA_conc_df.set_index('time', inplace=True)
            SA_conc_df['merged_total_SA_conc'] = pd.to_numeric(SA_conc_df['merged_total_SA_conc'], errors='coerce')
            SA_conc_df= SA_conc_df['merged_total_SA_conc'].resample(str(hravg)+'H',origin=origin).mean().reset_index()

        elif sheetname == 'NSA':
            mintemp = -21
            maxtemp = -31
            origin = pd.Timestamp('2021-10-01')
            SA_conc_df = pd.read_csv("E:/ExINP_Total_Graphing/nsasurfacearea.csv")
            SA_conc_df.dropna()
            saname = 'SA_m^2_L^-1'
            SA_conc_df.rename(columns={str(saname): 'merged_total_SA_conc'}, inplace=True)
            SA_conc_df['time'] = pd.to_datetime(SA_conc_df['time'])
            SA_conc_df = SA_conc_df[['time', 'merged_total_SA_conc']]
            SA_conc_df.set_index('time', inplace=True)
            SA_conc_df= SA_conc_df['merged_total_SA_conc'].resample(str(hravg)+'H',origin=origin).mean().reset_index()
            SA_conc_df['merged_total_SA_conc'] = SA_conc_df['merged_total_SA_conc'] * 1e-15

        if sheetname != 'GVB':
            data_filtered = data[~data['flag'].str.contains('FLAG', case=False, na=False)].copy()
        else:
            data_filtered = data

        data_filtered['time_reference'] = pd.to_datetime(data_filtered['time_reference'])

        data_filtered = data_filtered[(data_filtered['time_reference'] >= starttime)&(data_filtered['time_reference'] < stoptime)]

        data_filtered = data_filtered[['time_reference', 'T_min', 'INP_Conc']]
        data_filtered['T_min_rounded'] = data_filtered['T_min'].apply(lambda x: np.floor(x) if x < 0 else np.ceil(x))
        data_restricted = data_filtered[(data_filtered['T_min_rounded'] >= maxtemp) & (data_filtered['T_min_rounded'] <= mintemp)].copy()
        data_restricted['time_reference'] = pd.to_datetime(data_restricted['time_reference'])
        data_restricted.set_index('time_reference', inplace=True)

        result = []
        unique_temps = temperatures = np.arange(maxtemp, mintemp+1, 1)  
        for temp in unique_temps:
            temp_data = data_restricted[data_restricted['T_min_rounded'] == temp]
            if sheetname == 'ENA':
                resampled = temp_data['INP_Conc'].resample(str(hravg)+'H',origin=pd.Timestamp('2020-10-01')).mean()
            elif sheetname == 'SGP':
                resampled = temp_data['INP_Conc'].resample(str(hravg)+'H',origin=pd.Timestamp('2019-10-01')).mean()
            elif sheetname == 'NSA' or sheetname == 'GVB':
                resampled = temp_data['INP_Conc'].resample(str(hravg)+'H',origin=origin).mean()

            resampled_df = resampled.to_frame()
            resampled_df['T_min_rounded'] = temp
            result.append(resampled_df)

        data_restricted = pd.concat(result).reset_index()

        merged_df = pd.merge(data_restricted, SA_conc_df, left_on='time_reference', right_on='time')

        merged_df['INP_to_SA_ratio'] = merged_df['INP_Conc'] / merged_df['merged_total_SA_conc']
        merged_df.dropna()
        
        result_df = pd.DataFrame(columns=['T_min_rounded', 'time_reference', 'INP_to_SA_ratio', 'INP_to_SA_ratio_std', 'INP_to_SA_ratio_se'])
        time_range = pd.date_range(start=starttime, end=stoptime, freq=f'{hravg}H')
        for temp in range(maxtemp, mintemp+1): 
            for time in time_range:
                temp_df = merged_df[(merged_df['T_min_rounded'] == temp) & 
                                    ((merged_df['time_reference'] - time) < pd.Timedelta(hours=hravg/2)) & ((merged_df['time_reference'] - time) >= pd.Timedelta(hours=-(hravg/2)))]
                
                if not temp_df.empty:
                    inp_to_sa_ratio_mean = temp_df['INP_to_SA_ratio'].mean() if 'INP_to_SA_ratio' in temp_df else np.nan
                    inp_to_sa_ratio_std = temp_df['INP_to_SA_ratio'].std() if 'INP_to_SA_ratio' in temp_df else np.nan
                    inp_to_sa_ratio_se = inp_to_sa_ratio_std / np.sqrt(temp_df['INP_to_SA_ratio'].count()) if 'INP_to_SA_ratio' in temp_df and not temp_df['INP_to_SA_ratio'].isnull().all() else np.nan
                    
                    new_row = pd.DataFrame({
                        'T_min_rounded': [temp],
                        'time_reference': [time],
                        'INP_to_SA_ratio': [inp_to_sa_ratio_mean],
                        'INP_to_SA_ratio_std': [inp_to_sa_ratio_std],
                        'INP_to_SA_ratio_se': [inp_to_sa_ratio_se]
                    })

                    result_df = pd.concat([result_df, new_row], ignore_index=True)

        print(result_df.head())  

        result_df.to_csv(f'E:/mar25/ExINP{sheetname}_{hravg}H_{time1}-{time2}_fig6.csv', index=False)