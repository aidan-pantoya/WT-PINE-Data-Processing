import os
import pandas as pd

# Gett]ing the directory of our CSV file.
directory = "/Users/coz/Desktop/College_Docs/Research"

def process_files_in_directory(directory):
    flagged_datetimes = []
    
    for filename in os.listdir(directory):
       if filename.endswith('.csv'):
           file_path = os.path.join(directory, filename)   #combines the directory path and the filename into a single valid file path, so that we can access it in python
           
    df = pd.read_csv(file_path)
    
    # Columns to check
    columns_to_check = ['F1fContaminateMentor_N61', 'F1fContaminateWindSpeed_N61', 
                    'F1fContaminateCPCHigh_N61', 'F1fContaminateCPCSpike_N61', 'F1fContaminateWindDirection_N61']


    for index, row in df.iterrows():
        if (row[columns_to_check] != 0).any():
            flagged_datetimes.append(row['DateTimeUTC'])
            print(row['DateTimeUTC'])
                    
    flagged_df = pd.DataFrame(flagged_datetimes, columns=["Flagged Datetime"])
    flagged_df['FLAG'] = 'FLAG'
    return flagged_df

combined_df = process_files_in_directory(directory)
print(combined_df)
combined_df.to_csv('/Users/coz/Desktop/College_Docs/Research/flagging_times_new.csv', index=False)
