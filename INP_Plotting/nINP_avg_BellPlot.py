import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import math


for sheetname in ['NSA']:#'ENA','SGP']:

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
		
		# starttime = pd.to_datetime('2021-12-01') # one year
		# stoptime = pd.to_datetime('2022-12-01')
		# time1 = '2021-12-01'
		# time2 =  '2022-12-01'

		# starttime = pd.to_datetime('2022-03-01') # spring
		# stoptime = pd.to_datetime('2022-06-01')
		# time1 = '2022-03-01'
		# time2 =  '2022-06-01'

		# starttime = pd.to_datetime('2022-06-01') # summer
		# stoptime = pd.to_datetime('2022-09-01')
		# time1 = '2022-06-01'
		# time2 =  '2022-09-01'

		starttime = pd.to_datetime('2022-09-01') # fall
		stoptime = pd.to_datetime('2022-12-01')
		time1 = '2022-09-01'
		time2 =  '2022-12-01'

		# starttime = pd.to_datetime('2021-12-01') # winter
		# stoptime = pd.to_datetime('2022-03-01')
		# time1 = '2021-12-01'
		# time2 =  '2022-03-01'

	for hravg in [6,12,24,48,72]:
		csv_input_path = "E:/ExINP_Total_Graphing/ExINP"+str(sheetname)+"_WTAMU_L1MERGED_v3.csv"
		maxtemp = -31
		if sheetname == 'ENA':
		    mintemp = -20
		elif sheetname == 'SGP':
		    mintemp = -15
		elif sheetname == 'GVB':
			mintemp = -21
			maxtemp = -33
			
		elif sheetname == 'NSA':
			mintemp = -21
			maxtemp = -31
			
		labeler = f'{sheetname} - {hravg}H, {starttime} - {stoptime}'
		data = pd.read_csv(csv_input_path)

		if sheetname == 'GVB':
			data['flag'] = data['flag'].astype(str)
		data_filtered = data[~data['flag'].str.contains('FLAG', case=False, na=False)].copy()
		data_filtered['time_reference'] = pd.to_datetime(data_filtered['time_reference'])
		if sheetname != 'GVB' and sheetname != 'NSA':
			data_filtered = data_filtered[data_filtered['time_reference']]
		data_filtered = data_filtered[(data_filtered['time_reference'] >= starttime)&(data_filtered['time_reference'] < stoptime)]
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

		n_temps = len(unique_temps)
		fig, axes = plt.subplots(nrows=1, ncols=n_temps, figsize=(15,9), sharey=True)
		ftsz = 30
		fig.suptitle(labeler,fontsize=ftsz)
		tcnt = None
		for i, temp in enumerate(sorted(unique_temps)):
		    temp_data = data_grouped[(data_grouped['T_min_rounded'] == temp)&data_grouped['INP_Conc'] >0]['INP_Conc']
		    if not temp_data.empty:
		        print('len temp:')
		        tcnt = len(temp_data)
		        print(tcnt)
		        if tcnt == None:
		        	tcnt = int(tcnt/30)
		        mu, std = norm.fit(temp_data)
		        xmin, xmax = min(temp_data), max(temp_data)
		        x = np.linspace(xmin, xmax, 100)
		        p = norm.pdf(x, mu, std)
		        
		        axes[i].plot(p, x, 'k', linewidth=2)
		        axes[i].hlines(mu,min(p),max(p)*2, colors='blue', linestyles='-', linewidth=2,label='Average')
		        axes[i].hlines(np.median(temp_data),min(p),max(p), colors='cyan', linestyles='-', linewidth=2,label='Median')
		        
		        n, bins, patches = axes[i].hist(temp_data, bins=tcnt, orientation="horizontal", density=True, alpha=0.8)
		        
		        axes[i].fill_betweenx(x, 0, p, alpha=0.3)
		        if temp % 2 ==0:
		           axes[i].set_title(f'{temp}°C', fontsize=ftsz-10)

		        axes[i].set_xlabel(f'\nn = {tcnt}', fontsize=ftsz-18)
		        axes[i].set_ylim([0.001,15000])
		        axes[i].set_yscale('log')
		        # axes[i].set_xlim([0,0.2])
		        # axes[i].set_xticks([])
		    
		axes[0].set_ylabel('INP Concentration',fontsize=ftsz)
		plt.tight_layout(rect=[0, 0.03, 1, 0.95])
		# axes[i].legend(fontsize=ftsz-5)

		plt.savefig("E:/NSA_3_27_2024/ExINP"+str(sheetname)+"_bell_INP_"+str(hravg)+f"Havg_{time1}-{time2}.png", dpi=300, bbox_inches='tight')

		# plt.show()