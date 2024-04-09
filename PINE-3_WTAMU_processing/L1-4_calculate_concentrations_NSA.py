# import modules
import re
import glob
import pine_l1
import pandas as pd
import openpyxl

def get_lgbk(fileName, number):
    wb = openpyxl.load_workbook(fileName)
    ws = wb.active
    for row in ws.iter_rows(min_col=3,max_col=4):
        if row[0].value == number:
            return row[1].value
    return 'Nope'

# to extract numbers in the file names
regex = re.compile(r'\d+')

# Caliberation file
calib = "F:/PINE_Python/Codes/welasc1_1_cal_range4_133.txt"

# Ice Threshold limits file
thresh = 'F:/ExINPNSA/NSA_Ice_TH.csv'

# Housekkeping files (reference operations not included)
hkplist = glob.glob('F:/ExINPNSA/ExINPNSA_WTAMU/2/df_PINE-3_ExINPNSA21_opid*_instrument_L1.txt')


# read the Ice-threshold file
Ice_th = pd.read_csv(thresh, sep=',', header=0)

########### Loop to generate Level-1 INP data for all PINE operations ########
# for hk in hkplist:

#     try:

#         # reading the housekeeping file name.
#         hkpfilename = os.path.splitext(os.path.basename(hk))[0]

#         # extracting the opid# from the housekeeping file name
#         numbers = regex.findall(hkpfilename)
#         opid = int(numbers[1])

#         # List of level-0 fidas file for a given operation
#         flist = glob.glob('/Volumes/Seagate Portable Drive/ENAL1_20201117/f100-1/df_PINE-3_ExINPENA_opid-' + str(opid) + '_*.txt')

#         op = '/Volumes/Seagate Portable Drive/ENAL1_20201117/Housekeeping_L1_20201117/Individual/pfr_PINE-3_ExINPENA_opid-' + str(opid) + '.txt'


#         """
#         Below two lines were Commented by Sandeep on Oct-22 2020
        
#         # read the ice threshold value for a given operation
#         #th = Ice_th['Ice_Th'][opid - 1]
#         """

#         """
#         Below two lines were added by Sandeep on Oct-22 2020
#         """
#         # read the ice threshold value for a given operation
#         th = Ice_th[Ice_th['Op#'] == int(opid)]['Ice_Th'].reset_index()
        
#         th = Ice_th['Ice_Th'][0]

#         # calling the function to calculate INP Level-1
#         op_f = pine_l1.inp_l1(flist, calib, hk, op, th)


#     except IOError:

#         print >> sys.stderr  # printing any error to know what happened
#         pass

# ########## generate Level-1 INP data for a single PINE operation#########
for i in range(1100, 2000):
   
            opid = int(i)   # operation id
            try:
    
                # List of level-0 fidas file for a given operation
                flist = glob.glob('F:/ExINPNSA/ExINPNSA21/L0_Data/f100-01/df_PINE-3_ExINPNSA21_opid-' + str(opid) + '_*.txt')
    
                op = 'F:/ExINPNSA/ExINPNSA21/L0_Data/pfr_PINE-3_ExINPNSA21_opid-' + str(opid) + '.txt'
    
                hk = 'F:/ExINPNSA/ExINPNSA_WTAMU/2/df_PINE-3_ExINPNSA21_opid-' + str(opid) + '_instrument_L1.txt' #'C:/Users/Research/Desktop/PINE_Python/2/df_PINE-3_ExINPSGP_opid-' + str(opid) + '_instrument_L1.txt'
    
                # read the ice threshold value for a given operation
                th = Ice_th['Ice_Th'][opid - 1]
    
                # calling the function to calculate INP Level-1
                op_f = pine_l1.inp_l1(flist, calib, hk, op, th)
            except Exception as e:
                print(e)
                continue
       
