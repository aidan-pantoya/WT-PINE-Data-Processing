import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

for sheetname in ['NSA']:
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

		# starttime = pd.to_datetime('2021-10-19') # two years
		# stoptime = pd.to_datetime('2024-01-01')
		# time1 = '2021-10-19'
		# time2 =  '2024-01-01'

		# ------------------------------------------------

		# starttime = pd.to_datetime('2021-12-01',format='%Y-%m-%d') # winter
		# stoptime = pd.to_datetime('2022-03-01',format='%Y-%m-%d')
		

		# starttime2 = pd.to_datetime('2022-12-01',format='%Y-%m-%d') 
		# stoptime2 = pd.to_datetime('2023-03-01',format='%Y-%m-%d')

		# season = 'Winter'
		

		# ------------------------------------------------

		
		# starttime = pd.to_datetime('2022-03-01',format='%Y-%m-%d') # spring
		# stoptime = pd.to_datetime('2022-06-01',format='%Y-%m-%d')
		

		# starttime2 = pd.to_datetime('2023-03-01',format='%Y-%m-%d') 
		# stoptime2 = pd.to_datetime('2023-06-01',format='%Y-%m-%d')

		# season = 'Spring'
		

		# ------------------------------------------------

		
		# starttime = pd.to_datetime('2022-06-01',format='%Y-%m-%d') # summer
		# stoptime = pd.to_datetime('2022-09-01',format='%Y-%m-%d')
		
		# starttime2 = pd.to_datetime('2023-06-01',format='%Y-%m-%d')
		# stoptime2 = pd.to_datetime('2023-09-01',format='%Y-%m-%d')

		# season = 'Summer'
		
		# ------------------------------------------------

		
		starttime = pd.to_datetime('2022-09-01',format='%Y-%m-%d') # fall
		stoptime = pd.to_datetime('2022-12-01',format='%Y-%m-%d')
		
		starttime2 = pd.to_datetime('2023-09-01',format='%Y-%m-%d') 
		stoptime2 = pd.to_datetime('2023-12-01',format='%Y-%m-%d')

		season = 'Fall'
		

	for hravg in [6]:
		csv_input_path = "F:/ExINPNSA/ExINPNSA_20211019_20240101_L1_MERGEDv3.csv"
		data = pd.read_csv(csv_input_path)
		maxtemp = -31
		labeler = None
		if sheetname == 'ENA':
		    mintemp = -20
		elif sheetname == 'SGP':
		    mintemp = -15
		elif sheetname == 'GVB':
			mintemp = -22
			maxtemp = -33
		elif sheetname == 'NSA':
			mintemp = -21
			maxtemp = -31

		if sheetname == 'ENA':
			file_path = "E:/ExINP_Total_Graphing/nINP_ENA_SGP_MAX_MIN_v1.xlsx"
			df = pd.read_excel(file_path, sheet_name=sheetname)
			df = df[df.iloc[:, 0].apply(lambda x: x.is_integer() and x < 0 and x >=-31 and x<=mintemp)]
			labeler = 'C.'

		elif sheetname == 'SGP':
			file_path = "E:/ExINP_Total_Graphing/nINP_ENA_SGP_MAX_MIN.csv"
			df = pd.read_csv(file_path)
			df = df[df.iloc[:, 0].apply(lambda x: x < 0 and x >=maxtemp and x<=mintemp)]
			labeler = 'A.'

		if sheetname == 'SGP' or sheetname == 'ENA':
			range_temperatures = df.iloc[:, 0] 
			range_max_values = df.iloc[:, 1]    
			range_min_values = df.iloc[:, 2]  
		
		if sheetname == 'GVB':
			data['flag'] = data['flag'].astype(str)

		# try:
		# 	data_filtered = data[~data['flag'].str.contains('FLAG', case=False, na=False)].copy()
		# except:

		# WindDirection CPCSpike CPCHigh WindSpeed Mentor Operational
		flgtyp = ''

		data_filtered = data[~data['Flag'].str.contains(f'FLAG - {flgtyp}', case=False, na=False)].copy()

		print(data_filtered.count())

		# data_filtered = data

		if labeler == None:
			labeler = f'{sheetname} - {hravg}H, {season}'

		data_filtered['time_reference'] = pd.to_datetime(data_filtered['time_reference'])
		if sheetname != 'GVB' and sheetname != 'NSA':
			data_filtered = data_filtered[data_filtered['time_reference']]

		data_filtered = data_filtered[((data_filtered['time_reference'] >= starttime)&(data_filtered['time_reference'] < stoptime)) | ((data_filtered['time_reference'] >= starttime2)&(data_filtered['time_reference'] < stoptime2))]

		# data_filtered = data_filtered[(data_filtered['time_reference'] >= starttime)&(data_filtered['time_reference'] < stoptime)]


		print(data_filtered['time_reference'])


		data_filtered = data_filtered[['time_reference', 'T_min', 'INP_Conc']]
		data_filtered['T_min_rounded'] = data_filtered['T_min'].apply(lambda x: np.floor(x) if x < 0 else np.ceil(x))
		data_restricted = data_filtered[(data_filtered['T_min_rounded'] >= maxtemp) & (data_filtered['T_min_rounded'] <= mintemp)& (data_filtered['INP_Conc'] > 0)].copy()
		data_restricted.set_index('time_reference', inplace=True)

		result = []
		unique_temps = data_restricted['T_min_rounded'].unique()
		for temp in unique_temps:
		    temp_data = data_restricted[data_restricted['T_min_rounded'] == temp]
		    resampled = temp_data['INP_Conc'].resample(str(hravg)+'H').mean().dropna()  
		    resampled_df = resampled.to_frame()  
		    resampled_df['T_min_rounded'] = temp  
		    result.append(resampled_df)

		data_grouped = pd.concat(result).reset_index()

		# data_to_plot = [data_grouped[(data_grouped['T_min_rounded'] == t)&(data_grouped['INP_Conc']>0)]['INP_Conc'] for t in sorted(unique_temps)]

		data_to_plot = [data_grouped[(data_grouped['T_min_rounded'] == t)]['INP_Conc'] for t in sorted(unique_temps)]

		plt.figure(figsize=(15, 9))
		ftsz = 30
		# plt.plot(bestft_temps,fvals)
		plt.boxplot(data_to_plot, positions=sorted(unique_temps), showmeans=True, meanline=True,whis=[5,95])
		if sheetname == 'SGP' or sheetname == 'ENA':
			plt.fill_between(range_temperatures, range_max_values, range_min_values, color='gray', alpha=0.15)
		if sheetname == 'GVB' or sheetname == 'NSA':
			file_path = "E:/ExINP_Total_Graphing/Arctic_nINP_Min_Max.xlsx"
			df = pd.read_excel(file_path)
			df = df[df.iloc[:, 0].apply(lambda x: x < 0 and x >=maxtemp and x<=mintemp)]
			range_temperatures = df.iloc[:, 0] 
			range_max_values = df.iloc[:, 1]    
			range_min_values = df.iloc[:, 2]  
			plt.fill_between(range_temperatures, range_max_values, range_min_values, color='gray', alpha=0.15)

		plt.title(str(labeler), fontsize=15)#ftsz)
		plt.xlabel('T °C', fontsize=ftsz)
		plt.ylabel('INP Concentration', fontsize=ftsz)
		plt.yscale('log')
		ax = plt.gca()
		ax.tick_params(axis='x', labelsize=ftsz)
		ax.tick_params(axis='y', labelsize=ftsz)
		plt.xticks(range(maxtemp, mintemp+1,2), range(maxtemp, mintemp+1,2)) 
		if True: #sheetname != 'NSA':
			ax.set_ylim([0.001,1000])
		else:
			ax.set_ylim([0.01,100000])
		plt.grid(True, which="major", ls="--")
		# plt.savefig("E:/NSA_3_27_2024/ExINP"+str(sheetname)+"_INP_"+str(hravg)+f"Havg_{time1}-{time2}.png")
		plt.show()