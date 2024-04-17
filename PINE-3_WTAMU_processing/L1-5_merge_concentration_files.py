import glob
import natsort
import pandas as pd

inp_l1__file_list = glob.glob( 'F:/ExINPNSA/ExINPNSA_WTAMU/4/pfr_PINE-3_ExINPNSA21_opid-*_L1.txt')
inp_l1__file_list = natsort.natsorted(inp_l1__file_list)
inp1 = pd.read_csv(inp_l1__file_list[0], sep = '\t', header= 0)

for file in inp_l1__file_list[1:len(inp_l1__file_list)]:
    print(file)
    ft = pd.read_csv(file, sep = '\t', header= 0)
    inp1 = pd.concat([inp1, ft], ignore_index=True)

inp1.to_csv('F:/ExINPNSA/ExINPNSA_WTAMU/5/pfr_PINE-3_ExINPNSA21_opid-MERGED_L1.txt', header=True, index=False, sep = '\t')