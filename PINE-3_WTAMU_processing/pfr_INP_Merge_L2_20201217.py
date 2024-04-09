
import glob
import natsort
import pandas as pd

newList = []

#Merging of all operations run-wise INP L-2 files
flist = glob.glob('C:/Users/Research/Desktop/PINE_Python/L2/*.txt') #L2 indv.
for j in flist:
  for w in range(279,500):
    if 'ExINPSGP_opid-'+str(w)+'_' in j:
      newList.append(j) 
      break

flist = natsort.natsorted(newList)

xx = 1
# read the first file
print(flist)
f1 = pd.read_csv(flist[0], sep = '\t', header= xx)

# merging all the Level-2 files
for f in flist[1:len(flist)]:
    print('on file: '+str(f))
    ft = pd.read_csv(f, sep = '\t', header= xx)
    f1 = pd.concat([f1, ft], ignore_index=True)

f1.head() # fist few rows of the merged file

# save the merged PINE INP Level-2 file
f1.to_csv('C:/Users/Research/Desktop/PINE_Python/L2b/pfr_PINE-3_ExINPSGP_opid-MERGED2_L3.txt', header=True, index=False, sep = '\t')
