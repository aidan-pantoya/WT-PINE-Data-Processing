import pandas as pd
import numpy as np

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
        starttime = pd.to_datetime('2021-12-01') # one year
        stoptime = pd.to_datetime('2022-12-01')
        time1 = '2021-12-01'
        time2 =  '2022-12-01'
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

    for hravg in [6]:#,12,24,48,72]:

        csvpath = f"E:/NSA_3_27_2024/ExINP{sheetname}_SA_INP_{hravg}hr_{time1}_{time2}.csv"

        if sheetname == 'ENA':
            df = pd.read_csv(csvpath)  

            filtered_df = df[df['T_min_rounded'].isin([-20, -25, -30])]

            time_range = pd.date_range(start='10/01/2020', end='12/01/2020', freq=f'{hravg}H')
            new_df = pd.DataFrame(time_range, columns=['time_reference'])

            filtered_df['time_reference'] = pd.to_datetime(filtered_df['time_reference'])

            for temp in [-30, -25, -20]:
                new_df[f'INP_conc_{temp}'] = np.nan
                new_df[f'INP_to_SA_ratio_{temp}'] = np.nan

            for _, row in filtered_df.iterrows():
                for temp in [-30, -25, -20]:
                    if row['T_min_rounded'] == temp:
                        idx = new_df.index[new_df['time_reference'] == row['time_reference']].tolist()
                        if idx: 
                            new_df.at[idx[0], f'INP_conc_{temp}'] = row['INP_Conc_L^-1']
                            new_df.at[idx[0], f'INP_to_SA_ratio_{temp}'] = row['INP_to_SA_ratio']

            print(new_df.head()) 
            
        elif sheetname == 'SGP':
            df = pd.read_csv(csvpath)  

            filtered_df = df[df['T_min_rounded'].isin([-15,-20, -25, -30])]

            time_range = pd.date_range(start='10/1/2019', end='11/15/2019', freq=f'{hravg}H')
            new_df = pd.DataFrame(time_range, columns=['time_reference'])

            filtered_df['time_reference'] = pd.to_datetime(filtered_df['time_reference'])

            for temp in [-30, -25, -20,-15]:
                new_df[f'INP_conc_{temp}'] = np.nan
                new_df[f'INP_to_SA_ratio_{temp}'] = np.nan

            for _, row in filtered_df.iterrows():
                for temp in [-30, -25, -20,-15]:
                    if row['T_min_rounded'] == temp:
                        idx = new_df.index[new_df['time_reference'] == row['time_reference']].tolist()
                        if idx: 
                            new_df.at[idx[0], f'INP_conc_{temp}'] = row['INP_Conc_L^-1']
                            new_df.at[idx[0], f'INP_to_SA_ratio_{temp}'] = row['INP_to_SA_ratio']

            print(new_df.head()) 

        elif sheetname == 'GVB':
            df = pd.read_csv(csvpath)  

            filtered_df = df[df['T_min_rounded'].isin([-25, -30])]

            time_range = pd.date_range(start=starttime, end=stoptime, freq=f'{hravg}H')
            new_df = pd.DataFrame(time_range, columns=['time_reference'])

            filtered_df['time_reference'] = pd.to_datetime(filtered_df['time_reference'])

            for temp in [-30, -25]:
                new_df[f'INP_conc_{temp}'] = np.nan
                new_df[f'INP_to_SA_ratio_{temp}'] = np.nan

            for _, row in filtered_df.iterrows():
                for temp in [-30, -25]:
                    if row['T_min_rounded'] == temp:
                        idx = new_df.index[new_df['time_reference'] == row['time_reference']].tolist()
                        if idx: 
                            new_df.at[idx[0], f'INP_conc_{temp}'] = row['INP_Conc_L^-1']
                            new_df.at[idx[0], f'INP_to_SA_ratio_{temp}'] = row['INP_to_SA_ratio']

            print(new_df.head()) 

        elif sheetname == 'NSA':
            df = pd.read_csv(csvpath)  

            filtered_df = df[df['T_min_rounded'].isin([-15,-20,-25,-30])]

            time_range = pd.date_range(start=starttime, end=stoptime, freq=f'{hravg}H')
            new_df = pd.DataFrame(time_range, columns=['time_reference'])

            filtered_df['time_reference'] = pd.to_datetime(filtered_df['time_reference'])

            for temp in [-15,-20,-25,-30]:
                new_df[f'INP_conc_{temp}'] = np.nan
                new_df[f'INP_to_SA_ratio_{temp}'] = np.nan

            for _, row in filtered_df.iterrows():
                for temp in [-15,-20,-25,-30]:
                    if row['T_min_rounded'] == temp:
                        idx = new_df.index[new_df['time_reference'] == row['time_reference']].tolist()
                        if idx: 
                            new_df.at[idx[0], f'INP_conc_{temp}'] = row['INP_Conc_L^-1']
                            new_df.at[idx[0], f'INP_to_SA_ratio_{temp}'] = row['INP_to_SA_ratio']

            print(new_df.head()) 

        new_df.to_csv(f'E:/NSA_3_27_2024/ExINP_{sheetname}_{hravg}H_{time1}-{time2}_fig4_split.csv', index=False)
        new_df.dropna()

        medians = new_df.median()
        print(medians)

        # Initialize lists to store rows for above and below medians DataFrames
        above_medians_rows = []
        below_medians_rows = []

        # Indices of the specific columns to check (3rd, 5th, 7th) - Python uses 0-based indexing
        specific_column_indices = [2, 4, 6]

        for index, row in new_df.iterrows():
            # Check if the values in the specified columns are all above or below their respective medians
            if all(row[new_df.columns[column_index]] >= medians[column_index] for column_index in specific_column_indices if pd.notna(row[new_df.columns[column_index]])):
                above_medians_rows.append(row)
            elif all(row[new_df.columns[column_index]] <= medians[column_index] for column_index in specific_column_indices if pd.notna(row[new_df.columns[column_index]])):
                below_medians_rows.append(row)

        above_medians_df = pd.DataFrame(above_medians_rows, columns=new_df.columns).reset_index(drop=True)
        below_medians_df = pd.DataFrame(below_medians_rows, columns=new_df.columns).reset_index(drop=True)

        above_medians_df.to_csv(f'E:/NSA_3_27_2024/ExINP_{sheetname}_{hravg}H_{time1}-{time2}_fig4_HIGHINP.csv', index=False)
        below_medians_df.to_csv(f'E:/NSA_3_27_2024/ExINP_{sheetname}_{hravg}H_{time1}-{time2}_fig4_LOWINP.csv', index=False)