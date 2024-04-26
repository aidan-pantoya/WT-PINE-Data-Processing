"""

This python document computes PINE Level-1 (hereafter L1) INP concentrations (per liter of air) from fidas, operation, housekeeping, and ice-threshold files.

Additional major changes are made in this python document, specifically the addition of a new column 'Reference_Time', this column represents the median time from 'Flush mode'.

From now on, INP measurements are presented/visualized at 'Reference Time' (whereas in the previous versions of PINE L1 data, INP measurements are presented at 'time efill').

NOTE: Previous python document for L1 data generation is on 2020-03-26.

"""

import os
import re
import sys
import natsort
import numpy as np
import pandas as pd

regex = re.compile(r'\d+')

def inp_l1(flist, calib, hkp, op, th):
    col_names1 = ['Date_Time', 'Unknown_Value', 'Channel#', 'Pulse', 'Dp', 'Particle_Type']
    col_names2 = ['Channel#', 'Dp']
    categories = np.array(['Aerosol', 'Cloud Droplet', 'INP'])
    dtype1 = {'Unknown_Value': np.float16, 'Pulse': np.float16, 'Channel#': np.uint16, 'Dp': np.float16,
              'Particle_Type': 'category'}


    new_title2 = os.path.splitext(os.path.basename(op))[0]                        
    opd = pd.read_csv(op, sep='\t', header=0)                                       # read the operation file
    hkd = pd.read_csv(hkp, sep='\t', header=0)                                      # read the housekeeping file
    calib_data = pd.read_csv(calib, sep='\t', names=col_names2, header=None,        # read the calibration file
                             dtype={'Channel#': np.uint16, 'Dp': np.float16})

    # Synchronizing all the time stamps in operation file to local SGP time
    opd['time start'] = pd.to_datetime(opd['time start'])# - pd.to_timedelta(104, unit='s')
    opd['time expansion'] = pd.to_datetime(opd['time expansion'])# - pd.to_timedelta(104, unit='s')
    opd['time refill'] = pd.to_datetime(opd['time refill'])# - pd.to_timedelta(104, unit='s')
    opd['time end'] = pd.to_datetime(opd['time end']) #- pd.to_timedelta(104, unit='s')

    opd['Exp_Air_Vol'] = np.NaN
    opd['Bkgr_Air_Vol'] = np.NaN
    opd['Bkgr_INP'] = np.NaN
    opd['Bkgr_INP_Conc'] = np.NaN
    opd['INP_Count'] = np.NaN
    opd['INP_Conc'] = np.NaN
    opd['Air_Top_T'] = np.NaN
    opd['Air_Middle_T'] = np.NaN
    opd['Air_Bottom_T'] = np.NaN
    opd['Dew_Point_T'] = np.NaN
    opd['Pch']            = np.NaN
    opd['Ice_Threshold']  = np.NaN
    opd['Reference_Time'] = np.NaN

    for s in opd.index:
        opd.loc[s, 'Exp_Air_Vol'] = (pd.Timedelta(opd.loc[s, 'time refill'] -
                                                        opd.loc[s, 'time expansion']).seconds / 60) * opd.loc[
                                              s, 'flow expansion']

    opd.loc[:, 'Bkgr_Air_Vol'] = opd.loc[:, 'flow flush'] * 1.50

    l = 0                                                       
    flist = natsort.natsorted(flist)                             
    for f in flist[0:len(flist) - 1]:
        fpd = pd.read_csv(f, sep='\t', header=None, names=col_names1,
                          usecols=['Date_Time', 'Channel#', 'Dp', 'Particle_Type'], encoding='unicode_escape',
                          engine='python', dtype=dtype1)
        fpd['Date_Time'] = pd.to_datetime(fpd['Date_Time'])
        #fpd['Date_Time'] = pd.to_datetime(fpd['Date_Time']) - pd.to_timedelta(104, unit='s')                       # synchronizing the PINE time to local SGP time

        for j in calib_data.index:
            mask2 = (calib_data.loc[j, 'Channel#'] == fpd['Channel#'])
            fpd.loc[mask2, 'Dp'] = calib_data.loc[j, 'Dp']


        fpd.Particle_Type = pd.Categorical(fpd.Particle_Type, categories=categories)                           
        mask3 = (fpd['Dp'] < 5)                             
        mask4 = (5 <= fpd['Dp']) & (fpd['Dp'] <= th)       
        mask5 = (fpd['Dp'] > th)                         
        
        fpd.loc[mask3, 'Particle_Type'] = 'Aerosol'
        fpd.loc[mask4, 'Particle_Type'] = 'Cloud Droplet'
        fpd.loc[mask5, 'Particle_Type'] = 'INP'

        mask6 = (fpd['Date_Time'] >= opd.loc[l, 'time expansion']) & \
                (fpd['Date_Time'] <= opd.loc[l, 'time refill']) & (fpd['Particle_Type'] == 'INP')
        mask7 = (fpd['Date_Time'] >= opd.loc[l, 'time expansion'] - pd.to_timedelta(90, unit='s')) & \
                (fpd['Date_Time'] <= opd.loc[l, 'time expansion']) & (fpd['Particle_Type'] == 'INP')

        mask8 = (fpd['Date_Time'] >= opd.loc[l, 'time start']) & \
                (fpd['Date_Time'] <= opd.loc[l, 'time expansion'])

        # opd.loc[l, 'Reference_Time'] = fpd.loc[mask8, 'Date_Time'].median()

        flush_time = fpd.loc[mask8, 'Date_Time'].unique().tolist()
        flush_time = pd.to_datetime(flush_time)
        median = np.median(flush_time.to_numpy().astype(np.int64))

        opd.loc[l, 'Reference_Time'] = pd.Timestamp(median)

        opd.loc[l, 'INP_Count'] = fpd.loc[mask6, 'Particle_Type'].count()
        opd.loc[l, 'Bkgr_INP'] = fpd.loc[mask7, 'Particle_Type'].count()
        opd.loc[l, 'Bkgr_INP_Conc'] = opd.loc[l, 'Bkgr_INP'] / opd.loc[l, 'Bkgr_Air_Vol']
        opd.loc[l, 'INP_Conc'] = opd.loc[l, 'INP_Count'] / opd.loc[l, 'Exp_Air_Vol']
        opd['Ice_Threshold'] = th


        l += 1


    hka = np.loadtxt(hkp, delimiter='\t', skiprows=1, dtype=np.str_)

    for j in range(0, len(opd), 1):
        for k in range(0, len(hka), 1):

            try:

                if (np.datetime64(opd.iloc[j, 3]) == np.datetime64(hka[k, 0])):
                    opd.iloc[j, 17] = hka[k, 2]
                    opd.iloc[j, 18] = hka[k, 3]
                    opd.iloc[j, 19] = hka[k, 10]
                    opd.iloc[j, 20] = hka[k, 7]
                else:

                    continue

            except:
                pass


    opd.rename(columns={'time start': 'time_start', 'time expansion': 'time_expansion', 'time refill': 'time_refill',
                        'time end': 'time_end', 'flow flush': 'flow_flush', 'duration flush': 'duration_flush',
                        'flow expansion': 'flow_expansion', 'end pressure': 'end_pressure',
                        'Unnamed:10': 'Empty_column'}, inplace=True)

    opd.to_csv('F:/ExINPNSA/ExINPNSA_WTAMU/4/' + new_title2 + '_L1.txt', # MAKE NEW FOLDER, AND CHANGE DIRECTORY FOR IT AND FILENAME
               header=True, index=False, sep='\t')

    return opd


