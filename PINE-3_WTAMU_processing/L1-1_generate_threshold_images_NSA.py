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
    col_names1 = ['Date_Time', 'Unknown_Value', 'Channel#', 'Pulse', 'Dp', 'Particle_Type']
    col_names2 = ['Channel#', 'Dp']
    dtype1 = {'Unknown_Value': np.float16, 'Pulse': np.float16, 'Channel#': np.uint16, 'Dp': np.float16, 'Particle_Type': 'category'}
    calib_data = pd.read_csv(calib, sep = '\t', names=col_names2, header=None, dtype = {'Channel#':np.uint16, 'Dp':np.float16})
    flist = natsort.natsorted(flist)     
    fig, (ax1) = plt.subplots(1, 1, sharex=True, figsize=(17, 10))
    fig.autofmt_xdate()
    xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')

    for f in flist:
        print(f)
        new_title1 = os.path.splitext(os.path.basename(f))[0]

        fpd = pd.read_csv(f, sep='\t', header=None, names=col_names1, usecols=['Date_Time', 'Channel#', 'Dp', 'Particle_Type'],
                          encoding = 'unicode_escape', engine='python', dtype=dtype1)
        fpd['Date_Time'] = pd.to_datetime(fpd['Date_Time']) #- pd.to_timedelta(104, unit='s')


        for i in calib_data.index:
            mask1 = calib_data.loc[i, 'Channel#'] == fpd['Channel#']
            fpd.loc[mask1, 'Dp'] = calib_data.loc[i, 'Dp']

        fpd.columns = ['Date_Time', 'Channel#', 'Dp', 'Particle_Type']
        ax1.plot(np.array(fpd['Date_Time']), np.array(fpd['Dp']),'.',color = 'black')
        ax1.xaxis.set_major_formatter(xfmt)                                             
        ax1.tick_params(direction='in', bottom=True, top=True, left=True, right=True)
        ax1.set_ylabel(r'$Dp#$')
        ax1.grid(axis='x')

        if f == flist[len(flist) - 1]:

            plt.setp(ax1.get_xticklabels(), rotation=-45)
            plt.suptitle(''+ new_title1 +'')

            plt.savefig('F:/ExINPNSA/ExINPNSA_WTAMU/plots/' + new_title1 + '_L1.png', format='png', dpi=800)

    return

#  Calibration file(welas-133)
calib = "F:/PINE_Python/Codes/welasc1_1_cal_range4_133.txt"

# 165, 210, 223, 253, 283, 294, 364, 374, 391, 528, 553, 576, 614, 651, 665, 670, \
#    683, 697, 700, 729, 822, 835, 894, 979, 1067,1075,1153,1170,1171,1178,1193,1195, \
#      1204, 1210, 1253, 1303, 1347  

opids = [1253]

for i in range(1,1236):
    flist = glob.glob('F:/ExINPNSA/ExINPNSA21/L0_Data/f100-01/df_PINE-3_ExINPNSA21_opid-'+str(i)+'_runid-*_.txt')
   
tsyncNthresh(flist, calib)
