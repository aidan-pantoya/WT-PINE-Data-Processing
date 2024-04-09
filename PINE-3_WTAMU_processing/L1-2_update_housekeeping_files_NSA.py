#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 18:13:28 2020
 
@author: sandeepvepuri
"""

import os
import glob
import numpy as np
import pandas as pd


def hskptimesync(hkplist):
 
    for file in hkplist:

        new_title3 = os.path.splitext(os.path.basename(file))[0]
        hkd = pd.read_csv(file, sep= '\t', header=0, engine='python')
        hkd['date and time'] = pd.to_datetime(hkd['date and time']) - pd.to_timedelta(104, unit='s')        
        hkd['Rh_w(%)'] = (6.112*np.exp(17.62*(hkd['DP'])/(hkd['DP'] + 243.12)))/(6.112*np.exp(17.62*(hkd['Ti2'])/(hkd['Ti2'] + 243.12)))*100
        hkd['Rh_i(%)'] = (6.112*np.exp(22.46*(hkd['DP'])/(hkd['DP'] + 272.62)))/(6.112*np.exp(22.46*(hkd['Ti2'])/(hkd['Ti2'] + 272.62)))*100

        hkd.rename(columns={'date and time': 'Date_and_Time', 'Unnamed: 11': 'Empty_column', 'Rh_w(%)': 'RH_w',
                           'Rh_i(%)': 'RH_ice'}, inplace=True)

        hkd.to_csv("F:/ExINPNSA/ExINPNSA_WTAMU/2/" + new_title3 + '_L1.txt', header=True, index=False, sep = '\t')
            
        
# Listing all the housekeeping files (for loop added Dec 3 2021 by Elise Wilbourn)
for i in range(1, 2000):
    opid = int(i)   # operation id

    # List of level-0 fidas file for a given operation
    hkplist = glob.glob('F:/ExINPNSA/ExINPNSA21/L0_Data/housekeeping/df_PINE-3_ExINPNSA21_opid-' + str(opid) + '_instrument.txt')

    hskptimesync(hkplist)
    
# To calculate L1 housekeeping for entire range of files, comment out for loop (lines 32-39)
    #and uncomment lines 43-46
    
# hkplist = glob.glob('/Volumes/Seagate Portable Drive/NSA L1 Data/L0_Data/housekeeping/*_instrument.txt')

# Calling the housekeeping L1 funtion
# hskptimesync(hkplist)
