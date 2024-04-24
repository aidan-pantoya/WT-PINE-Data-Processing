import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import os
from sklearn.metrics import r2_score
from numpy.polynomial.polynomial import Polynomial
import matplotlib.ticker as ticker
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import sys

def evaluate_parameters(a, b, c, d, temperatures, medians):
    func_values = [np.exp(a * np.exp(-np.exp(b * (T + c))) + d) for T in temperatures]
    current_r2 = r2_score(medians, func_values)
    return current_r2, {'a': a, 'b': b, 'c': c, 'd': d}, func_values

def parse_date(date_str):
    for fmt in ('%d/%m/%Y %H:%M', '%d/%m/%y %H:%M'): 
        try:
            return pd.to_datetime(date_str, format=fmt).tz_localize('UTC')
        except ValueError:
            continue
    raise ValueError(f"Date format for {date_str} not recognized.")

# ENA times: 10/1/2020 - 3/28/2021

# SGP times: 10/1/2019 - 11/14/2019

# NSA times: 10/21/2021 - 4/30/2023
		# NSA SA: 10/01/2021 - 11/26/2022

# GVB times: 3/15/2023 - 4/10/2023

def run_through(hravg,sheetname):
	csv_input_path = f"E:/ExINP_Total_Graphing/ExINP{sheetname}_WTAMU_L1MERGED_v3.csv"
	data = pd.read_csv(csv_input_path)
	maxtemp = -31
	if sheetname == 'GVB':

		starttime = pd.to_datetime('2023-03-15').tz_localize('UTC')
		stoptime = pd.to_datetime('2023-04-11').tz_localize('UTC')
		time1 = '2023-03-15'
		time2 =  '2023-04-11'

		# starttime = pd.to_datetime('2023-03-15').tz_localize('UTC')
		# stoptime = pd.to_datetime('2023-04-01').tz_localize('UTC')
		# time1 = '2023-03-15'
		# time2 =  '2023-04-01'

		# starttime = pd.to_datetime('2023-04-01').tz_localize('UTC')
		# stoptime = pd.to_datetime('2023-04-11').tz_localize('UTC')
		# time1 = '2023-04-01'
		# time2 =  '2023-04-11'

	elif sheetname == 'NSA':
				# NSA times: 10/21/2021 - 4/30/2023
					# NSA SA: 10/01/2021 - 11/26/2022

		starttime = pd.to_datetime('2021-12-01') # one year
		stoptime = pd.to_datetime('2022-12-01')
		time1 = '2021-12-01'
		time2 =  '2022-12-01'

		# starttime = pd.to_datetime('2021-12-01') # winter
		# stoptime = pd.to_datetime('2022-03-01')
		# time1 = '2021-12-01'
		# time2 =  '2022-03-01'

		# starttime = pd.to_datetime('2022-03-01') # spring
		# stoptime = pd.to_datetime('2022-06-01')
		# time1 = '2022-03-01'
		# time2 =  '2022-06-01'

		# starttime = pd.to_datetime('2022-06-01') # summer
		# stoptime = pd.to_datetime('2022-09-01')
		# time1 = '2022-06-01'
		# time2 =  '2022-09-01'

		# starttime = pd.to_datetime('2022-09-22') # fall
		# stoptime = pd.to_datetime('2022-12-01')
		# time1 = '2022-09-01'
		# time2 =  '2022-12-01'


	elif sheetname == 'SGP':
		starttime = pd.to_datetime('2019-10-01')
		stoptime = pd.to_datetime('2019-11-15')
	elif sheetname == 'ENA':
		starttime = pd.to_datetime('2020-10-01')
		stoptime = pd.to_datetime('2021-04-01')

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
		print(SA_conc_df['time'])
		SA_conc_df = SA_conc_df[~SA_conc_df['merged_total_SA_conc'].str.contains('VALUE', case=False, na=False)].copy()
		SA_conc_df.set_index('time', inplace=True)
		SA_conc_df['merged_total_SA_conc'] = pd.to_numeric(SA_conc_df['merged_total_SA_conc'], errors='coerce')
		SA_conc_df= SA_conc_df['merged_total_SA_conc'].resample(str(hravg)+'H',origin=origin).mean().reset_index()

	elif sheetname == 'NSA':
		mintemp = -14
		maxtemp = -33
		origin = starttime
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
		data_filtered = data[~data['flag'].str.contains('FLAG', case=False, na=False)].copy()
	else:
		data_filtered = data

	data_filtered['time_reference'] = pd.to_datetime(data_filtered['time_reference'])
	data_filtered = data_filtered[(data_filtered['time_reference'] >= starttime)&(data_filtered['time_reference'] < stoptime)].copy()
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
	medians = []
	errors = []
	temperatures = np.arange(maxtemp, mintemp+1, 1)  

	for t in temperatures:  
	    values = merged_df[(merged_df['T_min_rounded'] == t)&(merged_df['INP_to_SA_ratio'] >0)]['INP_to_SA_ratio'].copy()
	    median = np.nanmedian(values)
	    sem = stats.sem(values, nan_policy='omit') 
	    medians.append(median)
	    errors.append(sem)
	    
	print(medians)
	best_r2 = -np.inf
	best_params = {'a': None, 'b': None, 'c': None, 'd': None}
	best_func_values = None

	a1,a2 = 10,30
	b1,b2 = 0.01,0.2
	c1,c2 = 1,30
	d1,d2 = 0.5,5

	traffic = 2

	a_range = np.arange(a1, a2,(a2-a1)/traffic)
	b_range = np.arange(b1,b2, (b2-b1)/traffic)
	c_range = np.arange(c1,c2, (c2-c1)/traffic)
	d_range = np.arange(d1,d2, (d2-d1)/traffic)

	if hravg == 6 and sheetname == 'SGP':
		a_range = np.arange(23.46, 23.46+1,1)
		b_range = np.arange(0.041,0.041+1,1)
		c_range = np.arange(12.9,12.9+1,1)
		d_range = np.arange(2.1,2.1+1,1)
	elif hravg == 6 and sheetname == 'ENA':
		a_range = np.arange(22, 22+1,1)
		b_range = np.arange(0.105,0.105+1,1)
		c_range = np.arange(9.7,9.7+1,1)
		d_range = np.arange(0.95,0.95+1,1)
		
	with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
	    futures = [executor.submit(evaluate_parameters, round(a,3), round(b,3), round(c,3), round(d,3), temperatures, medians)
	               for a in a_range for b in b_range for c in c_range for d in d_range]

	    concurrent.futures.wait(futures)
	    for future in futures:
	        current_r2, params, func_values = future.result()
	        if current_r2 > best_r2:
	            best_r2 = current_r2
	            best_params = params
	            best_func_values = func_values

	if best_params:
		a,b,c,d = best_params['a'],best_params['b'],best_params['c'],best_params['d']
		best_r2 = round(best_r2,4)
		print(f'{hravg}hr avg: Best R2: {best_r2}, Params: {best_params}')
		plt.figure(figsize=(20, 8))
		plt.plot(temperatures, best_func_values, label=f"Best Fit: a={best_params['a']}, b={best_params['b']}, c={best_params['c']}, d={best_params['d']}, R^2={best_r2}")
		plt.errorbar(temperatures, medians, yerr=errors, fmt='o', ecolor='b', capthick=2, capsize=5, linestyle='None', markersize=7)
		if sheetname == 'NSA':
			plt.title(f'ExINP{sheetname} - {hravg}hr IAF by Temp °C, {starttime} - {stoptime}', fontsize=25)
			plt.ylabel('IAF', fontsize=25)
		else:
			plt.title(f'ExINP{sheetname} - {hravg}hr INP/SA conc by Temp °C, {starttime} - {stoptime}', fontsize=25)
			plt.ylabel('INP/SA ratio', fontsize=25)
		plt.xlabel('Temp °C', fontsize=25)
		plt.xticks(temperatures, temperatures)
		plt.grid(True, which="major", ls="--")
		plt.legend(fontsize=20)
		plt.yscale('log') 
		if sheetname == 'GVB' or sheetname == 'NSA':
			plt.ylim([10000000,150000000000])
		else:
			plt.ylim([100000000,100000000000])

	# plt.savefig(f"E:/NSA_3_27_2024/ExINP{sheetname}_SA_INP_{hravg}hr_{time1}-{time2}_Trend.png")
	# plt.show()

	output_df = merged_df[['time_reference', 'INP_Conc', 'merged_total_SA_conc', 'T_min_rounded','INP_to_SA_ratio']].copy()
	output_df.rename(columns={'INP_Conc': 'INP_Conc_L^-1', 'merged_total_SA_conc': str(sheetname)}, inplace=True)

	output_csv_path = f"E:/NSA_3_27_2024/ExINP{sheetname}_SA_INP_{hravg}hr_{time1}_{time2}.csv"
	output_df.to_csv(output_csv_path, index=False)


for sheetname in ['NSA']:#'SGP','ENA']:
	for hravg in [6,12,24,48,72]:
		run_through(hravg,sheetname)