import time
import glob
import natsort
import pandas as pd
    
hlist = glob.glob('F:/ExINPNSA/ExINPNSA_WTAMU/2/df_PINE-3_ExINPNSA21_opid*.txt')
hlist = natsort.natsorted(hlist)   
start = time.time()

h1 = pd.read_csv(hlist[0], sep = '\t', header= 0)

for h in hlist[1:len(hlist)]:
    print(h)
    ht = pd.read_csv(h, sep = '\t', header= 0)
    h1 = pd.concat([h1, ht], ignore_index=True)

    elapsed = time.time()

end = time.time()

print(f'Time elapsed: {end-start} seconds')

h1.to_csv('F:/ExINPNSA/ExINPNSA_WTAMU/3/df_PINE-3_ExINPNSA21_opid-Reference_MEASUREMENTSMERGED_instrument_L1.txt', header=True, index=False, sep = '\t')