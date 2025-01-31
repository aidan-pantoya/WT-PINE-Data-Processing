import glob
import pine_l1
import pandas as pd

# def find_operation_type(file_path, target_value):  # THIS FUNCTION IS USED TAKING OUT BACKGROUND MEASUREMENTS
#     df = pd.read_excel(file_path)
#     operation_column = df.columns[2]  # GOES THROUGH THE THIRD COLUMN, FOR OPID
#     operation_type_column = df.columns[4]  # GOES THROUGH THE FIFTH COLUMN, FOR TYPE
#     match = df[df[operation_column] == target_value]
    
#     if not match.empty:
#         return match.iloc[0][operation_type_column]
#     else:
#         return "No match found"

calib = "F:/PINE_Python/Codes/welasc1_1_cal_range4_133.txt" # PATH TO CALIBRATION FILE
thresh = 'F:/ExINPNSA/NSA_Ice_TH.csv' # PATH TO ICE THRESHOLDS - CREATED IN L1-1
Ice_th = pd.read_csv(thresh, sep=',', header=0)

# ########## generate Level-1 INP data for a single PINE operation#########

# logbook = "F:/ExINPNSA/ExINPNSA21/Logbook_ExINPNSA21.xlsx"
        
for i in range(1000,1236): # RANGE OF OPIDS TO RUN
    opid = int(i)
    # op_type = str(find_operation_type(logbook, opid))
    # print(op_type)
    # if 'Temp' in op_type or 'Const' in op_type:

    try:
        flist = glob.glob('F:/ExINPNSA/ExINPNSA21/L0_Data/f100-01/df_PINE-3_ExINPNSA21_opid-' + str(opid) + '_*.txt') # FILES FOR F100
        op = 'F:/ExINPNSA/ExINPNSA21/L0_Data/pfr_PINE-3_ExINPNSA21_opid-' + str(opid) + '.txt' # FILES FOR OPERATION SETUP
        hk = 'F:/ExINPNSA/ExINPNSA_WTAMU/2/df_PINE-3_ExINPNSA21_opid-' + str(opid) + '_instrument_L1.txt' # FILES FOR HOUSEKEEPING
        th = Ice_th['Ice_Th'][int(opid) - 1]
        print(f'opid: {opid} ice th: {th}')
        op_f = pine_l1.inp_l1(flist, calib, hk, op, th)
    except Exception as e:
        print(e)
        continue
