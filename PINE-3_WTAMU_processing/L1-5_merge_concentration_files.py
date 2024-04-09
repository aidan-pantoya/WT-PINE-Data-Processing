#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: sandeepvepuri
"""

import glob
import natsort
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from plotly.offline import plot
pio.orca.config.executable = '/opt/anaconda3/lib/orca.app/Contents/MacOS/orca'
pio.orca.config.save()

# List of INP Level-1 files
inp_l1__file_list = glob.glob( 'D:/ExINPSGP/ExINPSGP_measurements_WTAMU/4'   )#'C:/Users/Research/Desktop/PINE_Python/4/pfr_PINE-3_ExINPSGP_opid-*_L1.txt')
inp_l1__file_list = natsort.natsorted(inp_l1__file_list)


# Reading the first Level-1 INP file form the list
inp1 = pd.read_csv(inp_l1__file_list[0], sep = '\t', header= 0)


for file in inp_l1__file_list[1:len(inp_l1__file_list)]:
    ft = pd.read_csv(file, sep = '\t', header= 0)
    inp1 = pd.concat([inp1, ft], ignore_index=True)


# Saving the Merged INP Level-1 file
inp1.to_csv('C:/Users/Research/Desktop/PINE_Python/5/pfr_PINE-3_ExINPSGP_opid-MERGED_L1.txt', header=True, index=False, sep = '\t')
