"""
Created on Fri Feb 21 08:57:30 2020

@author: sandeepvepuri
"""

import re
import os
import natsort
import numpy as np
import pandas as pd




#Defining PINE INP_L1_b function
def inp_l1_b(flist, calib, op, hkp, th, folder):

    #Specifying the columns and headers
    col_names1 = ['Date_Time', 'Unknown_Value', 'Channel#', 'Pulse', 'Dp', 'Particle_Type']
    col_names2 = ['Channel#', 'Dp']

    #Array with the particle categories and datatypes
    categories = np.array(['Aerosol', 'Cloud Droplet', 'Ice Crystal'])
    dtype1 = {'Unknown_Value': np.float16, 'Pulse': np.float16, 'Channel#': np.uint16, 'Dp': np.float16,
              'Particle_Type': 'category'}

    #Reading the filename from 'INP_L1' file
    new_title2 = os.path.splitext(os.path.basename(op))[0]
   

    #Reading the OPID number from the 'INP_L1_a' file
    regex = re.compile('\d+')
    numbs = regex.findall(new_title2)
   
    opid = int(numbs[1])  # Reading the operation ID from the filename # BE CAREFUL WITH NUMBERS

    #Reading the INP_L1 data
    opd = pd.read_csv(op, sep='\t', header=0)
    opd['time_expansion'] = pd.to_datetime(opd['time_expansion'])

    #Reading the Houskeeping_L1 data
    hkd = pd.read_csv(hkp, sep='\t', header=0)
    hkd['Date_and_Time'] = pd.to_datetime(hkd['Date_and_Time'])

    #Reading the welas_range4-133 calibration file
    calib_data = pd.read_csv(calib, sep='\t', names=col_names2, header=None,
                             dtype={'Channel#': np.uint16, 'Dp': np.float16})


    l = 0

    #Sorting the fidas list
    flist = natsort.natsorted(flist)



    for f in flist[0:len(flist) - 1]:

        #Creating an empty INP dataframe
        inp = pd.DataFrame(
            columns=['time_stamp', 'Air_Middle_T', 'Air_Bottom_T', 'Dew_Point_T', 'Pch',
                     'RH_ice', 'RH_w', 'Bkgr_INP', 'Bkgr_INP_Conc', 'INP_Count',
                     'INP_Conc', 'Reference_Time'])
        inp['time_stamp'] = pd.to_datetime(inp['time_stamp'])

        ninp = pd.DataFrame(
            columns=['time_stamp', 'Air_Middle_T', 'Air_Bottom_T', 'Dew_Point_T', 'Pch',
                     'RH_ice', 'RH_w', 'INP_Count', 'INP_Conc', 'Reference_Time'])
        ninp['time_stamp'] = pd.to_datetime(ninp['time_stamp'])


        #Reading the fidas file
        fpd = pd.read_csv(f, sep='\t', header=None, names=col_names1,
                          usecols=['Date_Time', 'Channel#', 'Dp', 'Particle_Type'], encoding='unicode_escape',
                          engine='python', dtype=dtype1)
        fpd['Date_Time'] = pd.to_datetime(fpd['Date_Time'])

        #Time Synchronization of the fidas file.
        fpd['Date_Time'] = pd.to_datetime(fpd['Date_Time']) - pd.to_timedelta(104, unit='s')

        #Calibrating the fidas data
        for j in calib_data.index:
            mask2 = (calib_data.loc[j, 'Channel#'] == fpd['Channel#'])
            fpd.loc[mask2, 'Dp'] = calib_data.loc[j, 'Dp']

        fpd.Particle_Type = pd.Categorical(fpd.Particle_Type, categories=categories)

        #Masking and categorizing the fidas data based on the size threshold
        mask3 = (fpd['Dp'] < 5)
        mask4 = (5 <= fpd['Dp']) & (fpd['Dp'] <= th)
        mask5 = (fpd['Dp'] > th)
        fpd.loc[mask3, 'Particle_Type'] = 'Aerosol'
        fpd.loc[mask4, 'Particle_Type'] = 'Cloud Droplet'
        fpd.loc[mask5, 'Particle_Type'] = 'Ice Crystal'

        #Masking run-wise housekeeping data
        mask6 = (hkd['Date_and_Time'] >= opd.loc[l, 'time_expansion']) & (
                    hkd['Date_and_Time'] <= opd.loc[l, 'time_refill'])
        inp['time_stamp'] = hkd.loc[mask6, 'Date_and_Time']
        inp['Air_Middle_T'] = hkd.loc[mask6, 'Ti2']
        inp['Air_Bottom_T'] = hkd.loc[mask6, 'Ti3']
        inp['Dew_Point_T'] = hkd.loc[mask6, 'DP']
        inp['Pch'] = hkd.loc[mask6, 'Pch']
        inp['RH_ice'] = hkd.loc[mask6, 'RH_ice']
        inp['RH_w'] = hkd.loc[mask6, 'RH_w']
        inp['Bkgr_INP'] = opd.loc[l, 'Bkgr_INP']
        inp['Bkgr_INP_Conc'] = opd.loc[l, 'Bkgr_INP_Conc']
        inp['Reference_Time'] = opd.loc[l, 'Reference_Time']
        inp = inp.reset_index()
        del inp['index']

        #Counting the Ice particles run-wise
        for k in range(0, len(inp)):
            mask7 = (fpd['Date_Time'] == inp.loc[k, 'time_stamp']) & (fpd['Particle_Type'] == 'Ice Crystal')
            inp.loc[k, 'INP_Count'] = fpd.loc[mask7, 'Particle_Type'].count()



        #ninp.loc[0, :] = inp.iloc[0]
        #ninp.loc[0, 'Ice Crystal Conc. (L^-1 Air)'] = float((ninp.loc[0, 'Ice Crystal Count']) / ((pd.Timedelta(
        #   ninp.loc[0, 'time_stamp'] - (opd.loc[l, 'time expansion'] - pd.to_timedelta(1, unit='s'))).seconds / 60) *
        #                                                                                             opd.loc[
        #                                                                                              l, 'flow flush']))


        r = l + 1  # 'r' is the RUN number


        #Saving the INP_L1_b file
        inp.to_csv(os.path.join(folder, 'pfr_PINE-3_ExINPSGP_opid-%d_RUN-%d_L1_b.txt' %(opid, r)), header=True,
                   index=False, sep='\t')


        l += 1


    return inp




#Defining the function for generation of PINE INP_L2 data from PINE INP_L1_b
def inp_l2(file, folder):


    dim = len(file)
    l = 0

    #Creating an empty plotly figure
    # fig = make_subplots(specs=[[{"secondary_y": False}]])
    file = natsort.natsorted(file)

    #Looping over run-wise INP_L1_b file of a single operation
    for f in file:

        title = os.path.splitext(os.path.basename(f))[0]
	print(title)
        #Reading the OPID number from the 'INP_L1_b' filename
        regex = re.compile('\d+')
        numbs = regex.findall(title)
        opid = int(numbs[1])  # Reading the operation ID from the filename # BE CAREFUL WITH NUMBERS

        # new_title2 = title[0:28]

        #Reading the PINE INP_L1_b run-wise file
        l1_b = pd.read_csv(f, sep='\t', header=0)
        l1_b['time_stamp'] = pd.to_datetime(l1_b['time_stamp'])
        min_indx = l1_b[['Air_Middle_T']].idxmin()  #Finding the index for the minimum AMT value.
        l1_b.loc[int(min_indx):, 'Air_Middle_T'] = l1_b['Air_Middle_T'].min() #Setting all the AMTs above the 'min_indx' to min. AMT (dC).


        l1_c = pd.DataFrame(columns=['time_stamp', 'INP_Count'])   #Creating an empty dataframe


        # Binning every 0.5 dC AMT.
        bins = np.arange(0, -36.5, -0.5)
        l1_b['bin'] = pd.cut(l1_b['Air_Middle_T'], bins=bins[::-1], include_lowest=True, right=False)

        #Calculating the time difference for each temp. bin
        time_diff = l1_b.groupby(l1_b['bin'])['time_stamp'].apply(lambda x: (
                                                                                x.max() - x.min()).seconds / 60).reset_index()  # Start time equals to the bin opening temperature (open bracket)
        l1_c['INP_Count'] = l1_b.groupby('bin')['INP_Count'].sum()
        l1_c['time_stamp'] = l1_b.groupby('bin')['time_stamp'].max()     #The time_stamp is the time refill corresponding to the each bin-edge AMT (dC)
        l1_c = l1_c.reset_index()

        #Merging INP_Count and Housekkeping data based on the bin-edge temperature
        l2 = pd.merge(l1_c, l1_b.iloc[:, 0:7], how='left', on=['time_stamp'])

        #Adding the column of Volume (= 3 Litres) expanded in each bin to PINE INP_L2 data
        l2['Vol'] = time_diff['time_stamp'] * 3
        l2 = l2.dropna()
        l2 = l2.sort_values('time_stamp', ascending=True)
        l2 = l2.reset_index()
        del l2['index']

        #Compensating for the missed volume(L) expanded from one bin-edge timestamp to the start time of the following bin
        l2.loc[1:, 'Vol'] = l2.loc[1:, 'Vol'] + 0.05
        l2['INP_Conc'] = l2['INP_Count'] / l2['Vol']
        l2['Bin_Edge_T'] = l2['bin'].apply(lambda x: x.left)
        l2['Cumul_Vol'] = l2['Vol'].cumsum()
        l2['Bkgr_INP'] = l1_b['Bkgr_INP']
        l2['Bkgr_INP_Conc'] = l1_b['Bkgr_INP_Conc']
        l2['Reference_Time'] = l1_b['Reference_Time']
        l2['Cumul_INP_Count'] = l2['INP_Count'].cumsum()
        l2['Cumul_INP_Conc'] = l2['Cumul_INP_Count'] / l2['Cumul_Vol']


        r = l + 1  # 'r' is the RUN number



        # save the PINE L2 data
        l2.to_csv(os.path.join(folder, 'pfr_PINE-3_ExINPSGP_opid-%d_RUN-%d_L2.txt' %(opid, r)), header=True,
                  index=False, sep='\t')

        l += 1


