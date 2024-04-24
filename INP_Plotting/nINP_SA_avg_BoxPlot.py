import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import os
from sklearn.metrics import r2_score
from numpy.polynomial.polynomial import Polynomial

sheetnames = ['NSA']#'SGP','ENA']

 # ENA times: 10/1/2020 - 3/28/2021

 # SGP times: 10/1/2019 - 11/14/2019

 # NSA times: 10/21/2021 - 4/30/2023

 # GVB times: 3/15/2023 - 4/10/2023

def parse_date(date_str):
    for fmt in ('%d/%m/%Y %H:%M', '%d/%m/%y %H:%M'): 
        try:
            return pd.to_datetime(date_str, format=fmt).tz_localize('UTC')
        except ValueError:
            continue
    raise ValueError(f"Date format for {date_str} not recognized.")

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

	if sheetname == 'NSA':
		timeperiods = []
		starttime = pd.to_datetime('2021-10-18',format='%Y-%m-%d') # one year
		stoptime = pd.to_datetime('2022-12-01',format='%Y-%m-%d')
		time1 = ''
		time2 =  ''
		timeperiods.append([starttime,stoptime,time1,time2])

		# starttime = pd.to_datetime('2021-12-01') # winter
		# stoptime = pd.to_datetime('2022-03-01')
		# time1 = '2021-12-01'
		# time2 =  '2022-03-01'
		# timeperiods.append([starttime,stoptime,time1,time2])
		# starttime = pd.to_datetime('2022-03-01') # spring
		# stoptime = pd.to_datetime('2022-06-01')
		# time1 = '2022-03-01'
		# time2 =  '2022-06-01'
		# timeperiods.append([starttime,stoptime,time1,time2])
		# starttime = pd.to_datetime('2022-06-01') # summer
		# stoptime = pd.to_datetime('2022-09-01')
		# time1 = '2022-06-01'
		# time2 =  '2022-09-01'
		# timeperiods.append([starttime,stoptime,time1,time2])
		# starttime = pd.to_datetime('2022-09-01') # fall
		# stoptime = pd.to_datetime('2022-12-01')
		# time1 = '2022-09-01'
		# time2 =  '2022-12-01'
		# timeperiods.append([starttime,stoptime,time1,time2])

	elif sheetname == 'SGP':
		starttime = pd.to_datetime('2019-10-01')
		stoptime = pd.to_datetime('2019-11-15')
		time1 = '2019-10-01'
		time2 =  '2019-11-15'
	elif sheetname == 'ENA':
		starttime = pd.to_datetime('2020-10-01')
		stoptime = pd.to_datetime('2021-04-01')
		time1 = '2020-10-01'
		time2 =  '2021-04-01'

	for starttime,stoptime,time1,time2 in timeperiods:
		for hravg in [6]:
			stats_columns = ['median', 'average', '95%', '75%', '25%', '5%', 'above_95%', 'below_5%']
			stats_df = pd.DataFrame(columns=['T_min_rounded'] + stats_columns)

			csv_input_path = "E:/ExINP_Total_Graphing/ns_reference/Ullrich_curve_Desert_Dust.xlsx"
			data_ullrich = pd.read_excel(csv_input_path)

			csv_input_path = "E:/ExINP_Total_Graphing/ns_reference/Hiranuma_curve_NX_wet_dry.xlsx"
			NX_curve_dry = pd.read_excel(csv_input_path, sheet_name='Dry')
			NX_curve_wet = pd.read_excel(csv_input_path, sheet_name='Wet')

			csv_input_path = "E:/ExINP_Total_Graphing/ns_reference/Hiranuma_curve_MCC_wet_dry.xlsx"
			MCC_curve_dry = pd.read_excel(csv_input_path, sheet_name='Dry')
			MCC_curve_wet = pd.read_excel(csv_input_path, sheet_name='Wet')
			labeler = f'{sheetname} - {hravg}H'#, {starttime} - {stoptime}'
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
			csv_input_path =  "F:/ExINPNSA/ExINPNSA_20211019_20240101_L1_MERGEDv3.csv" #f"E:/ExINP_Total_Graphing/ExINP{sheetname}_WTAMU_L1MERGED_v3.csv"
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
				origin = pd.Timestamp('2023-03-15',tz='UTC')
				SA_conc_df = pd.read_csv("E:/ExINP_Total_Graphing/gvbsurfacearea.csv")
				SA_conc_df.dropna()
				saname = 'SA_m^2_L^-1'
				SA_conc_df.rename(columns={str(saname): 'merged_total_SA_conc'}, inplace=True)
				SA_conc_df['time'] = SA_conc_df['time'].apply(parse_date)
				SA_conc_df = SA_conc_df[['time', 'merged_total_SA_conc']]
				print(SA_conc_df['time'])
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
				SA_conc_df['merged_total_SA_conc'] = SA_conc_df['merged_total_SA_conc'] #* 1e-15

			if sheetname != 'GVB':
				try:
					data_filtered = data[~data['flag'].str.contains('FLAG', case=False, na=False)].copy()

				except:
					data_filtered = data[~data['Flag'].str.contains('FLAG', case=False, na=False)].copy()
			else:
				data_filtered = data

			print(data_filtered.count())

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

	#------------------------------------------------------------------
			

			data_ullrich = data_ullrich[(data_ullrich['Ullrich_DD_T_dC'] >= maxtemp) & (data_ullrich['Ullrich_DD_T_dC'] <= mintemp)].copy()
			ul_temp = data_ullrich.iloc[:, 1]    
			ul_y = data_ullrich.iloc[:, 2]   

			NX_curve_dry = NX_curve_dry[(NX_curve_dry['H15_NX_dry_log_T_dC'] >= maxtemp) & (NX_curve_dry['H15_NX_dry_log_T_dC'] <= mintemp)].copy()
			nx_dry_temp = NX_curve_dry.iloc[:, 0]    
			nx_dry_y = NX_curve_dry.iloc[:, 1]   

			NX_curve_wet = NX_curve_wet[(NX_curve_wet['H15_NX_wet_log_T_dC'] >= maxtemp) & (NX_curve_wet['H15_NX_wet_log_T_dC'] <= mintemp)].copy()
			nx_wet_temp = NX_curve_wet.iloc[:, 0]    
			nx_wet_y = NX_curve_wet.iloc[:, 1] 

			MCC_curve_dry = MCC_curve_dry[(MCC_curve_dry['H15_MCC_dry_T_dC'] >= maxtemp) & (MCC_curve_dry['H15_MCC_dry_T_dC'] <= mintemp)].copy()
			MCC_dry_temp = MCC_curve_dry.iloc[:, 0]    
			MCC_dry_y = MCC_curve_dry.iloc[:, 1]   

			MCC_curve_wet = MCC_curve_wet[(MCC_curve_wet['H19_MCC_AS_T'] >= maxtemp) & (MCC_curve_wet['H19_MCC_AS_T'] <= mintemp)].copy()
			MCC_wet_temp = MCC_curve_wet.iloc[:, 2]    
			MCC_wet_y = MCC_curve_wet.iloc[:, 3]   

			temps_Fe = []
			Fe_vals = []
			for tempFe in np.arange(-28,-10+0.1,0.1):
				Fe_val = np.exp(-0.545 *(tempFe)+1.0125)
				temps_Fe.append(tempFe)
				Fe_vals.append(Fe_val)

			temps_magn = []
			magn_vals = []
			for tempmag in np.arange(-25, -10 + 0.001, 0.1):
			    Magn = (1/2.2) * np.exp(15.6 * np.exp(-np.exp(0.139 * (tempmag + 19.56))) + 4.82)
			    temps_magn.append(tempmag)
			    magn_vals.append(Magn)


			# Agricultural Soil Dust:
			# For temperatures between -26.15 dC and -11.15 dC, n_s = exp( 110.266 - ( 0.35 (273.15+T) ) )
			temps_ag_soil = []
			ag_soil_vals = []
			for tempmag in np.arange(-26.15, -11.15+0.1, 0.1):
			    Magn = np.exp(110.266 - (0.35 *(273.15 + tempmag)))
			    temps_ag_soil.append(tempmag)
			    ag_soil_vals.append(Magn)

			
			result = []
			rows = []
			unique_temps = merged_df['T_min_rounded'].unique()
			for temp in unique_temps:
			    temp_data = merged_df[(merged_df['T_min_rounded'] == temp)&(merged_df['INP_Conc'] >0)]
			    resampled = temp_data['INP_Conc']
			    above_95 = resampled[resampled > resampled.quantile(0.95)].values
			    below_5 = resampled[resampled < resampled.quantile(0.05)].values

			    resampled_df = resampled.to_frame()
			    resampled_df['T_min_rounded'] = temp
			    result.append(resampled_df)
			    row = {
			    'T_min_rounded': temp,
			    'median': resampled.median(),
			    'average': resampled.mean(),
			    '95%': resampled.quantile(0.95),
			    '75%': resampled.quantile(0.75),
			    '25%': resampled.quantile(0.25),
			    '5%': resampled.quantile(0.05),
			    'above_95%': resampled[resampled > resampled.quantile(0.95)].count(),
			    'below_5%': resampled[resampled < resampled.quantile(0.05)].count()
			    }
			    for idx, val in enumerate(above_95, start=1):
			        row[f'above_95%_{idx}'] = val
			    for idx, val in enumerate(below_5, start=1):
			        row[f'below_5%_{idx}'] = val
			    rows.append(row)

			stats_df = pd.DataFrame(rows)
			# stats_csv_output_path = f"E:/mar25/ExINP_{sheetname}_{hravg}hr_INP_{time1}-{time2}_Stats_Summary.csv"
			# stats_df.to_csv(stats_csv_output_path, index=False)

			result = []
			rows = []
			unique_temps = merged_df['T_min_rounded'].unique().copy()
			for temp in unique_temps:
			    temp_data = merged_df[(merged_df['T_min_rounded'] == temp)&(merged_df['INP_to_SA_ratio'] >0)]
			    resampled = temp_data['INP_to_SA_ratio'] 
			    above_95 = resampled[resampled > resampled.quantile(0.95)].values
			    below_5 = resampled[resampled < resampled.quantile(0.05)].values
			    resampled_df = resampled.to_frame()
			    resampled_df['T_min_rounded'] = temp
			    result.append(resampled_df)
			    row = {
			    'T_min_rounded': temp,
			    'median': resampled.median(),
			    'average': resampled.mean(),
			    '95%': resampled.quantile(0.95),
			    '75%': resampled.quantile(0.75),
			    '25%': resampled.quantile(0.25),
			    '5%': resampled.quantile(0.05),
			    'above_95%': resampled[resampled > resampled.quantile(0.95)].count(),
			    'below_5%': resampled[resampled < resampled.quantile(0.05)].count()
			    }
			    for idx, val in enumerate(above_95, start=1):
			        row[f'above_95%_{idx}'] = val
			    for idx, val in enumerate(below_5, start=1):
			        row[f'below_5%_{idx}'] = val
			    rows.append(row)

			stats_df = pd.DataFrame(rows)
			# stats_csv_output_path = f"E:/mar25/ExINP_{sheetname}_{hravg}hr_INPSA_{time1}-{time2}_Stats_Summary.csv"
			# stats_df.to_csv(stats_csv_output_path, index=False)

			data_to_plot = []
			temperatures = np.arange(maxtemp, mintemp+1, 1) 
			unique_temps = sorted(data_restricted['T_min_rounded'].unique())

			for temp in temperatures:
			    if temp in unique_temps:
			        values = merged_df[(merged_df['T_min_rounded'] == temp)&(merged_df['INP_to_SA_ratio'] >0)]['INP_to_SA_ratio'].dropna()
			        data_to_plot.append(values.tolist())
			    else:
			        data_to_plot.append([])

			bestft_temps = []
			fvals = []
			for temp in unique_temps:
				fval = np.exp(a * np.exp(-np.exp(b * (temp + c))) + d)
				fvals.append(fval)
				bestft_temps.append(temp)

			plt.figure(figsize=(15,9))
			
			# plt.plot(ul_temp,ul_y,color='red',label='Desert Dust')

			# plt.plot(nx_dry_temp,nx_dry_y,color='orange')
			# plt.plot(nx_wet_temp,nx_wet_y,color='orange')
			good_nx_temps = []
			good_nx_wet = []
			good_nx_dry = []
			for x,y in zip(nx_dry_temp,nx_dry_y):
				for xx,yy in zip(nx_wet_temp,nx_wet_y):
					if x == xx:
						good_nx_dry.append(y)
						good_nx_wet.append(yy)
						good_nx_temps.append(x)


			# plt.fill_between(good_nx_temps,good_nx_dry,good_nx_wet,color='orange',alpha=0.2,label='NX')

			# plt.plot(MCC_dry_temp,MCC_dry_y,color='green')
			# plt.plot(MCC_wet_temp,MCC_wet_y,color='green')

			good_nx_temps = []
			good_nx_wet = []
			good_nx_dry = []
			for x,y in zip(MCC_dry_temp,MCC_dry_y):
				for xx,yy in zip(MCC_wet_temp,MCC_wet_y):
					if x == xx:
						good_nx_dry.append(y)
						good_nx_wet.append(yy)
						good_nx_temps.append(x)

			# plt.fill_between(good_nx_temps,good_nx_dry,good_nx_wet,color='green',alpha=0.2,label='MCC')


			# plt.plot(temps_Fe,Fe_vals,color='blue',label='Sea Spray')
			# plt.plot(temps_magn,magn_vals,color='pink',label='Magnetite')
			# plt.plot(bestft_temps,fvals,color='gray',label='Fit (This Study)')

			if sheetname == 'GVB':
				plt.plot(temps_ag_soil,ag_soil_vals,color='brown',label='Ag Soil')

			plt.boxplot(data_to_plot, positions=temperatures, showmeans=True, meanline=True, whis=[5, 95])
			xticktemps = temperatures.copy()
			
			xticktemps = [xt for xt in xticktemps if xt % 2 != 0]
			
			ftsz = 30
			plt.title(labeler, fontsize=ftsz)
			plt.xlabel('T °C', fontsize=ftsz)
			plt.ylabel('IAF', fontsize=ftsz)
			plt.yscale('log') 
			ax = plt.gca()
			ax.tick_params(axis='x', labelsize=ftsz)
			ax.tick_params(axis='y', labelsize=ftsz)
			plt.xticks(xticktemps, labels=[str(t) for t in xticktemps])
			if sheetname == 'GVB':
				ax.set_ylim([10000,2*10**12])
			elif sheetname == 'NSA':
				ax.set_ylim([0.000000001,0.01])
			elif sheetname == 'SGP' or sheetname == 'ENA':
				ax.set_ylim([1000,2*10**11])
			ax.set_xlim([maxtemp-1,mintemp+1])
			plt.grid(True, which="major", ls="--")
			plt.legend(fontsize=ftsz-5)#,loc='lower left')
			# plt.savefig(f"E:/NSA_329/ExINP{sheetname}_INP_SA_{hravg}Havg_{time1}-{time2}.png")
			plt.show()