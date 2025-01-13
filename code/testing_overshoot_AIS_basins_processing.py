####################################################################################
# Imports
import pandas as pd
import os
import fnmatch
import numpy as np
import pickle
import sys

####################################################################################

id=["cx209", "cy837", "cy838", "cz375", "cz376", "cz377"]

count = 0

####################################################################################

# Read ice sheet data

print("Getting ice sheet data...")

icesheet_d = {}

for i in id:

    AIS_data = {}

    print(f"Working on {i}...")

    AIS_stats = pd.read_csv(f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/testing_new_{i}_AIS_basins_diagnostics.csv")
    
    AIS_stats.time = AIS_stats.apply(lambda x: int(x.filename[105:109]), axis=1)

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

    ice_save_file = open('../processed_data/testing_AIS_basins_data.pkl', 'wb') 
    pickle.dump(icesheet_d, ice_save_file) 
    ice_save_file.close()

####################################################################################