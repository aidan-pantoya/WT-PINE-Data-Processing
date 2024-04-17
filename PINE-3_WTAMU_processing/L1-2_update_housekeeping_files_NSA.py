import os
import glob
import numpy as np
import pandas as pd

def find_operation_type(file_path, target_value):
    df = pd.read_excel(file_path)
    operation_column = df.columns[2]  
    operation_type_column = df.columns[4]  
    match = df[df[operation_column] == target_value]
    
    if not match.empty:
        return match.iloc[0][operation_type_column]
    else:
        return "No match found"

def hskptimesync(hkplist):
 
    for file in hkplist:

        new_title3 = os.path.splitext(os.path.basename(file))[0]
        hkd = pd.read_csv(file, sep= '\t', header=0, engine='python')
        hkd['date and time'] = pd.to_datetime(hkd['date and time']) #- pd.to_timedelta(104, unit='s')        
        hkd['Rh_w(%)'] = (6.112*np.exp(17.62*(hkd['DP'])/(hkd['DP'] + 243.12)))/(6.112*np.exp(17.62*(hkd['Ti2'])/(hkd['Ti2'] + 243.12)))*100
        hkd['Rh_i(%)'] = (6.112*np.exp(22.46*(hkd['DP'])/(hkd['DP'] + 272.62)))/(6.112*np.exp(22.46*(hkd['Ti2'])/(hkd['Ti2'] + 272.62)))*100

        hkd.rename(columns={'date and time': 'Date_and_Time', 'Unnamed: 11': 'Empty_column', 'Rh_w(%)': 'RH_w',
                           'Rh_i(%)': 'RH_ice'}, inplace=True)

        hkd.to_csv("F:/ExINPNSA/ExINPNSA_WTAMU/2/" + new_title3 + '_L1.txt', header=True, index=False, sep = '\t')
       
        
logbook = "F:\ExINPNSA\ExINPNSA21\Logbook_ExINPNSA21.xlsx"
        
for i in range(1000,1236):
    opid = int(i)
    
    op_type = str(find_operation_type(logbook, opid))
    print(op_type)
    
    if 'Temp' in op_type or 'Const' in op_type:
        hkplist = glob.glob('F:/ExINPNSA/ExINPNSA21/L0_Data/housekeeping/df_PINE-3_ExINPNSA21_opid-' + str(opid) + '_instrument.txt')
        hskptimesync(hkplist)