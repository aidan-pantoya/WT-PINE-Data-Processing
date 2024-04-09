#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: sandeepvepuri
"""
import time
import glob
import natsort
import pandas as pd

# list of all housekeeping files
hlist = glob.glob('C:/Users/Research/Desktop/PINE_Python/2/df_PINE-3_ExINPSGP_opid*.txt')
hlist = natsort.natsorted(hlist)   # sorting the list based on the filename

start = time.time()

# Reading the first housekeeping file from the list
h1 = pd.read_csv(hlist[0], sep = '\t', header= 0)


for h in hlist[1:len(hlist)]:
    ht = pd.read_csv(h, sep = '\t', header= 0)
    h1 = pd.concat([h1, ht], ignore_index=True)

    elapsed = time.time()

end = time.time()

print(f'Time elapsed: {end-start} seconds')


# save the merged file
h1.to_csv('C:/Users/Research/Desktop/PINE_Python/3'
          '/df_PINE-3_ExINPSGP_opid-Reference_MERGED_instrument_L1.txt', header=True, index=False, sep = '\t')