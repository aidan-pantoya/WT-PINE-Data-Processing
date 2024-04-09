
#Importing the modules
import re
import os
import glob
import natsort
import pandas as pd
import pine_l2


# Defining the output INP file directory path
dir_fidas = 'C:/Users/Research/Desktop/ExINPSGP/L0_Data/f100-01' # Path to Fidas files

dir_l1 = 'D:/ExINPSGP/ExINPSGP_measurements_WTAMU/4'     #'C:/Users/Research/Desktop/PINE_Python/4' #individual L1 file pathway

dir_l1_b = 'C:/Users/Research/Desktop/PINE_Python/L1b'  # Specify the directory to INP_L1_b output files.

dir_l2 ='C:/Users/Research/Desktop/PINE_Python/L2'    # Specify the directory to INP_L2 output files.

calib = 'C:/Users/Research/Desktop/PINE_Python/Codes/welasc1_1_cal_range4_133.txt' # Calibration file pathway

thresh = 'C:/Users/Research/Desktop/ExINPSGP/PINE/L1/SGP_Ice_TH.csv' # Ice Threshold file pathway

dir_hkp ='D:/ExINPSGP/ExINPSGP_measurements_WTAMU/2' #'C:/Users/Research/Desktop/PINE_Python/2' # Housekeeping Files pathway


# read the Ice Threshold file
Ice_th = pd.read_csv(thresh, sep=',', header=0)



# Use below code to generate L2 data for only One Operation file.
for i in range(198, 500):
    try:
    
        opid = int(i)   # operation id
        
        # list of fidas files
        flist = glob.glob(os.path.join(dir_fidas, 'df_PINE-3_ExINPSGP_opid-'+str(opid)+'_*.txt')) #change campaign name
        print("-----------------")
        print("fidas: "+str(flist))
        # Housekeeping L1 file
        hkp = (os.path.join(dir_hkp, 'df_PINE-3_ExINPSGP_opid-'+str(opid)+'_instrument_L1.txt')) #change campaign name
        print('-----------------')
        print("housekeeping: "+str(hkp))
        # operation L1 file
        op = (os.path.join(dir_l1,  'pfr_PINE-3_ExINPSGP_opid-' + str(opid) + '_L1.txt')) #change campaign name
        print('-----------------')
        print('ops: '+str(op))
        # read the ice threshold value for a given operation
        th = Ice_th['Ice_Th'][opid - 1]
        # Calling the PINE INP_L1_b function
        inp_l1_b = pine_l2.inp_l1_b(flist, calib, op, hkp, th, dir_l1_b)
        
        
        # Generating PINE INP_L2 data
        inp_l1_b_list =  glob.glob(os.path.join(dir_l1_b, 'pfr_PINE-3_ExINPSGP_opid-'+str(opid)+'_RUN*.txt')) #change campaign name
        inp_l1_b_list = natsort.natsorted(inp_l1_b_list)

        # Calling function for calculating PINE INP_L2
        pine_l2.inp_l2(inp_l1_b_list, dir_l2)
    except:
      continue





# # Use below FOR loop code to generate L2 data for multiple Operation files.

# # Generating PINE INP_l1_b data
# inp_l1_list =  glob.glob(os.path.join(dir_l1, 'pfr_PINE-3_ExINPENA_opid*.txt'))     # Lisitng all the PINE INP_L1_a files
# inp_l1_list = natsort.natsorted(inp_l1_list)


# # Generating PINE INP L2 data
#
# j=0
# # Looping over the Level-1 INP files
# for op in inp_l1_list:
#
#     # Reading the title of the INP_L1_a file
#     title = os.path.splitext(os.path.basename(op))[0]
#
#     # Extracting the OPID number in the INP_L1 filename
#     regex = re.compile('\d+')
#     numbs = regex.findall(title)
#     opid  = int(numbs[1])   # Reading the operation ID from the filename
#
#     flist = glob.glob(os.path.join(dir_fidas, 'df_PINE-3_ExINPENA_opid-'+str(opid)+'_*.txt'))
#     hkp = (os.path.join(dir_hkp, 'df_PINE-3_ExINPENA_opid-'+str(opid)+'_instrument_L1.txt'))
#
#
#     th = Ice_th['Ice_Th'][j]      # Ice Threshold File
#
#
#     # Calling the PINE INP_L1_b function
#     inp_l1_b = pine_l2.inp_l1_b(flist, calib, op, hkp, th, dir_l1_b)
#
#     j+=1
#
#
#
#     # Generating PINE INP_L2 data
#     inp_l1_b_list =  glob.glob(os.path.join(dir_l1_b,
#                            'pfr_PINE-3_ExINPENA_opid-'+str(opid)+'_RUN*.txt'))
#     inp_l1_b_list = natsort.natsorted(inp_l1_b_list)
#
#
#     # Calling function for calculating PINE INP_L2
#     pine_l2.inp_l2(inp_l1_b_list, dir_l2)

