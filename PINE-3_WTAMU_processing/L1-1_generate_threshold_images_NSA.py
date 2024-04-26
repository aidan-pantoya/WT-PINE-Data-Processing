import os
import glob
import natsort
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython import get_ipython

get_ipython().magic('reset -sf')

def tsyncNthresh(flist, calib):
    col_names1 = ['Date_Time', 'Unknown_Value', 'Channel#', 'Pulse', 'Dp', 'Particle_Type'] # HEADER NAMES OF FILE
    col_names2 = ['Channel#', 'Dp'] # CALIBRATION HEADER
    dtype1 = {'Unknown_Value': np.float16, 'Pulse': np.float16, 'Channel#': np.uint16, 'Dp': np.float16, 'Particle_Type': 'category'} # SETTING TYPES FOR CONVERTING F100 FILES WITH CALIBRATION
    calib_data = pd.read_csv(calib, sep = '\t', names=col_names2, header=None, dtype = {'Channel#':np.uint16, 'Dp':np.float16}) # READING IN CALIBRATION FILES
    flist = natsort.natsorted(flist)  # SORTING ALL F100 FILES
    fig, (ax1) = plt.subplots(1, 1, sharex=True, figsize=(17, 10)) # SETTING UP GRAPH
    fig.autofmt_xdate() # CREATING DATES FOR GRAPH
    xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S') # FORMATTING THE DATES

    for f in flist: # GOES THROUGH EACH FILE IN F1000 OPID LIST
        print(f) # PRINTS WHICH FILE WE ARE ON
        new_title1 = os.path.splitext(os.path.basename(f))[0]  # GET A TITLE FOR GRAPH



        fpd = pd.read_csv(f, sep='\t', header=None, names=col_names1, usecols=['Date_Time', 'Channel#', 'Dp', 'Particle_Type'],
                          encoding = 'unicode_escape', engine='python', dtype=dtype1) # READ IN THE CURRENT FILE

        fpd['Date_Time'] = pd.to_datetime(fpd['Date_Time']) #- pd.to_timedelta(104, unit='s') # USED IF YOU NEED TO CONVERT THE DATE


        for i in calib_data.index: # LOOP FOR CONVERTING THE PARTICLE CHANNELS AND Dps
            mask1 = calib_data.loc[i, 'Channel#'] == fpd['Channel#']
            fpd.loc[mask1, 'Dp'] = calib_data.loc[i, 'Dp']

        fpd.columns = ['Date_Time', 'Channel#', 'Dp', 'Particle_Type'] # plotting that information
        ax1.plot(np.array(fpd['Date_Time']), np.array(fpd['Dp']),'.',color = 'black')
        ax1.xaxis.set_major_formatter(xfmt)                                             
        ax1.tick_params(direction='in', bottom=True, top=True, left=True, right=True)
        ax1.set_ylabel(r'$Dp#$')
        ax1.grid(axis='x')

        if f == flist[len(flist) - 1]:

            plt.setp(ax1.get_xticklabels(), rotation=-45)
            plt.suptitle(''+ new_title1 +'')

            plt.savefig('F:/ExINPNSA/ExINPNSA_WTAMU/plots/' + new_title1 + '_L1.png', format='png', dpi=800) # saving the figure, YOU WILL NEED TO CHANGE THE DIRECTORY

    return

#  Calibration file(welas-133). YOU WILL NEED CHANGE DIRECTORY FOR YOUR CALIBRATION FILE
calib = "F:/PINE_Python/Codes/welasc1_1_cal_range4_133.txt"

# CHANGE THE OPIDS FOR YOUR OPERATIONS
opids = [1253]

for i in opids: # this can be used for running multiple OPIDS
    # CHANGE DIRECTORY TO F100 RUN-ID FILES, NAME SHOULD END WITH: _opid-'+str(i)+'_runid-*_.txt'
    flist = glob.glob('F:/ExINPNSA/ExINPNSA21/L0_Data/f100-01/df_PINE-3_ExINPNSA21_opid-'+str(i)+'_runid-*_.txt') 
   
tsyncNthresh(flist, calib)
