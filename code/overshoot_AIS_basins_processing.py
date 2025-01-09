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

####################################################################################

id=("cs568", "cx209", "cw988", "cw989", "cw990", "cy837", "cy838", "cz374", "cz375", "cz376", "cz377", "cz378", 
    "cz834", "cz855", "cz859", "db587", "db723", "db731", "da087", "da266", "db597", "db733", "dc324", 
    "cz944", "di335", "da800", "da697", "da892", "db223", "df453", "de620", "dc251", "db956", 
    "dc051", "dc052", "dc248", "dc249", "dc565", "dd210", "dc032", "df028", "de621", "dc123", "dc130", 
    "df025", "df027", "df021", "df023", "dh541", "dh859", "de943", "de962", "de963", "dk554", "dk555", "dk556")

count = 0

####################################################################################

# Read atmosphere data

atmos_d = {}

print("Getting atmosphere data...")

for i in id:

    print(f"Working on {i}...")

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

print("Getting ice sheet data...")

icesheet_d = {}

for i in id:

    AIS_data = {}

    print(f"Working on {i}...")

    AIS_stats = pd.read_csv(f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/new_{i}_AIS_basins_diagnostics.csv")

    if i == "cs568":    
         AIS_stats.time = AIS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)-100
    
    else:
        AIS_stats.time = AIS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)
        
    AIS_stats["global_T"] = np.nan

    count = 0

    for j in atmos_d["cx209"][:,0]:

        year = int(j+1) # because BISICLES stores data for 01/01 of following year...
        print(f"Working on year: {year}")
        pos = np.where(AIS_stats.time==year)

        if np.size(pos) > 0:
            AIS_stats["global_T"].mask(AIS_stats["time"]==year, atmos_d["cx209"][count,1], inplace=True)
        else:
            print(f"Year {year} not found in AIS data for {i}")

        count = count + 1

    # Interpolate to fill NaN valures in global_delta_T
    AIS_stats["global_T"].interpolate(method='linear', inplace=True)

    AIS_grounded_SMB = []
    AIS_floating_SMB = []
    AIS_floating_BMB = []
    AIS_GL_discharge = []
    AIS_grounded_vol = []
    AIS_floating_vol = []
    AIS_VAF = []
    
    count = 0

    for j in range(17):
        
        AIS_grounded_SMB.append(AIS_stats[(AIS_stats['maskNo'] == j) & (AIS_stats['region'] == 'grounded') & (AIS_stats['quantity'] == 'SMB')])
        AIS_floating_SMB.append(AIS_stats[(AIS_stats['maskNo'] == j) & (AIS_stats['region'] == 'floating') & (AIS_stats['quantity'] == 'SMB')])
        AIS_floating_BMB.append(AIS_stats[(AIS_stats['maskNo'] == j) & (AIS_stats['region'] == 'floating') & (AIS_stats['quantity'] == 'BMB')])
        AIS_GL_discharge.append(AIS_stats[(AIS_stats['maskNo'] == j) & (AIS_stats['region'] == 'grounded') & (AIS_stats['quantity'] == 'discharge')])
        AIS_grounded_vol.append(AIS_stats[(AIS_stats['maskNo'] == j) & (AIS_stats['region'] == 'grounded') & (AIS_stats['quantity'] == 'volume')])
        AIS_floating_vol.append(AIS_stats[(AIS_stats['maskNo'] == j) & (AIS_stats['region'] == 'floating') & (AIS_stats['quantity'] == 'volume')])
        AIS_VAF.append(AIS_stats[(AIS_stats['maskNo'] == j) & (AIS_stats['region'] == 'entire') & (AIS_stats['quantity'] == 'volumeAbove')])

        AIS_grounded_SMB[j].reset_index(drop=True, inplace=True)
        AIS_floating_SMB[j].reset_index(drop=True, inplace=True)
        AIS_floating_BMB[j].reset_index(drop=True, inplace=True)
        AIS_GL_discharge[j].reset_index(drop=True, inplace=True)
        AIS_grounded_vol[j].reset_index(drop=True, inplace=True)
        AIS_floating_vol[j].reset_index(drop=True, inplace=True)
        AIS_VAF[j].reset_index(drop=True, inplace=True)

        AIS_data[j] = pd.concat([AIS_grounded_SMB[j], AIS_floating_SMB[j], AIS_floating_BMB[j], AIS_GL_discharge[j], AIS_grounded_vol[j], AIS_floating_vol[j], AIS_VAF[j]], axis=1)

    count = count + 1
    
    icesheet_d[i] = AIS_data

####################################################################################

# Save ice sheet data

if count > 0:

    print("Saving ice sheet data to file...")

    ice_save_file = open('../processed_data/AIS_basins_data.pkl', 'wb') 
    pickle.dump(icesheet_d, ice_save_file) 
    ice_save_file.close()

####################################################################################