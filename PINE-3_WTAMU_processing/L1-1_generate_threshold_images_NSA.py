"""
Created on Tue Feb 11 09:18:34 2020
@author: sandeepvepuri
"""

import os
import glob
import natsort
import numpy as np
import pandas as pd
import plotly.io as pio
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython import get_ipython
pio.orca.config.executable = '/opt/anaconda3/lib/orca.app/Contents/MacOS/orca'
pio.orca.config.save()


# clear al the user created variables before executing the below code
get_ipython().magic('reset -sf')


# PINE fidas visulaization fucntion
def tsyncNthresh(flist, calib):

    # column names for the fidas and calibration files
    col_names1 = ['Date_Time', 'Unknown_Value', 'Channel#', 'Pulse', 'Dp', 'Particle_Type']
    col_names2 = ['Channel#', 'Dp']

    dtype1 = {'Unknown_Value': np.float16, 'Pulse': np.float16, 'Channel#': np.uint16, 'Dp': np.float16, 'Particle_Type': 'category'}

    # read the fidas calibration file
    calib_data = pd.read_csv(calib, sep = '\t', names=col_names2, header=None, dtype = {'Channel#':np.uint16, 'Dp':np.float16})

    flist = natsort.natsorted(flist)     # sort the RUN-wise fidas files by name

    """ These lines added by Sandeep on Oct-19 2020 """

    # Create a figure
    fig, (ax1) = plt.subplots(1, 1, sharex=True, figsize=(17, 10))
    # fig.text(0.5, 0.09, 'Local Time', ha='center', fontsize=15)
    fig.autofmt_xdate()
    # plt.subplots_adjust(hspace=.0)  # remove vertical gap between subplots
    xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')

    """ The above lines added by Sandeep on Oct-19 2020  """

    # loop over fidas files for a given operation
    for f in flist:
        print(f)
        new_title1 = os.path.splitext(os.path.basename(f))[0]

        fpd = pd.read_csv(f, sep='\t', header=None, names=col_names1, usecols=['Date_Time', 'Channel#', 'Dp', 'Particle_Type'],
                          encoding = 'unicode_escape', engine='python', dtype=dtype1)
        fpd['Date_Time'] = pd.to_datetime(fpd['Date_Time']) - pd.to_timedelta(104, unit='s')


        for i in calib_data.index:
            mask1 = calib_data.loc[i, 'Channel#'] == fpd['Channel#']
            fpd.loc[mask1, 'Dp'] = calib_data.loc[i, 'Dp']

        fpd.columns = ['Date_Time', 'Channel#', 'Dp', 'Particle_Type']

        """ These lines added by Sandeep on Oct-19 2020 """

        # plot time series of Fidas OPC data
        ax1.plot(np.array(fpd['Date_Time']), np.array(fpd['Dp']),'.',color = 'black')
        ax1.xaxis.set_major_formatter(xfmt)                                             # x-ais date foramting
        ax1.tick_params(direction='in', bottom=True, top=True, left=True, right=True)
        # ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
        # ax1.yaxis.get_major_ticks()[0].label1.set_visible(False)  # remove the first y-tick label
        ax1.set_ylabel(r'$Dp#$')
        ax1.grid(axis='x')

        if f == flist[len(flist) - 1]:

            plt.setp(ax1.get_xticklabels(), rotation=-45)
            plt.suptitle(''+ new_title1 +'')

            # save the figure
            plt.savefig('F:/ExINPNSA/ExINPNSA_WTAMU/plots/' + new_title1 + '_L1.png', format='png', dpi=800)

        """ The above lines added by Sandeep on Oct-19 2020  """
    return

#  Calibration file(welas-133)
calib = "F:/PINE_Python/Codes/welasc1_1_cal_range4_133.txt"

opids = [1186]
for i in opids:
    flist = glob.glob('F:/ExINPNSA/ExINPNSA21/L0_Data/f100-01/df_PINE-3_ExINPNSA21_opid-'+str(i)+'_runid-*_.txt')
   
     #flist = glob.glob('/media/adpanto/WTAMU_Hiranuma_ExINP_SGP_NSA/ExINPNSA/ExINPNSA21/L0_Data/f100-01/df_PINE-3_ExINPNSA21_opid-'+str(i)+'_runid-*_.txt')
    
            # Calling the threshold images generating funtion
tsyncNthresh(flist, calib)
