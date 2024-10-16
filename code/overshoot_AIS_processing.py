####################################################################################
# Imports
import cf
import cfplot as cfp
import pandas as pd
import os
import fnmatch
import numpy as np
import pickle
import sys

# from amrfile import io as amrio

####################################################################################


id = ["cs568", "cx209", "cy837", "cy838", "cz375", "cz376", "cz377", "dc052", "dc051", "df028", 
      "dc123", "dc130", "cw988", "cw989", "cw990","cy623", "da914", "da916", "da917"]

run_type = ["Ctrl","Ramp-Up 1", "1.5C", "2C", "3C", "4C", "5C", "_ramp-down -4 1.5C 50yr", 
            "_ramp-down -4 2C 50yr", "_ramp-down -4 3C 50yr", "_ramp-down -4 4C 50yr", 
            "_ramp-down -4 5C 50yr", "Ramp-Up 2", "Ramp-Up 3", "Ramp-Up 4", "Hist 1", 
            "Hist 2", "Hist 3", "Hist 4"]

runs = dict(zip(id, run_type)) 

count = 0

####################################################################################

# Read atmosphere data

atmos_d = {}

print("Getting atmosphere data...")

for i in id:

    print(f"Working on {i}: {runs[i]}")

    atmos_dir = f"/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/{i}/atmos/"
    atmos_files = sorted(os.listdir(atmos_dir))
    atmos_files_matched = fnmatch.filter(atmos_files, f"{i}*.pp")

    count = 0
    
    atmos_df = np.ndarray(shape = (len(atmos_files_matched),2))

    for j in atmos_files_matched:
        
        filename = f"{atmos_dir}/{j}"
        f = cf.read(filename)
        temp = f[0]
        temp_global_avg = temp.collapse('area: mean', weights=True)

        if i == "cs568":
            atmos_df[count, 0] = int(j[9:13])-100
        else:
            atmos_df[count, 0] = int(j[9:13])
            
        atmos_df[count, 1] = temp_global_avg.data

        count = count + 1
        
    atmos_d[i] = atmos_df

####################################################################################

# Save atmosphere data

if count > 0:
    print("Saving atmosphere data to file...")

    atmos_save_file = open('../processed_data/atmos_data.pkl', 'wb') 
    pickle.dump(atmos_d, atmos_save_file) 
    atmos_save_file.close() 

####################################################################################

# Read ice sheet data

initialT = atmos_d["cx209"][0,1]

print("Getting ice sheet data...")

icesheet_d = {}

for i in id:

    print(f"Working on {i}: {runs[i]}")

    AIS_stats = pd.read_csv(f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/new_{i}_AIS_diagnostics.csv")

    if i == "cs568":    
         AIS_stats.time = AIS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)-100
    
    else:
        AIS_stats.time = AIS_stats.apply(lambda x: int(x.file[97:101]), axis=1)

    AIS_stats["global_delta_T"] = np.nan

    count = 0

    for j in atmos_d[i][:,0]:

        year = int(j+1) # because BISICLES stores data for 01/01 of following year...
        print(f"Working on year: {year}")
        pos = np.where(AIS_stats.time==year)

        if np.size(pos) > 0:
            pos = pos[0][0]
            AIS_stats.at[pos,"global_delta_T"] = atmos_d[i][count,1]-initialT
        else:
            print(f"Year {year} not found in AIS data for {i}")

        count = count + 1

    # Interpolate to fill NaN valures in global_delta_T
    AIS_stats["global_delta_T"].interpolate(method='linear', inplace=True)

    icesheet_d[i] = AIS_stats

####################################################################################

# Save ice sheet data

if count > 0:

    print("Saving ice sheet data to file...")

    ice_save_file = open('../processed_data/icesheet_data.pkl', 'wb') 
    pickle.dump(icesheet_d, ice_save_file) 
    ice_save_file.close()

####################################################################################