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


id = ["cs568", "cx209", "cw988", "cw989", "cw990", "cy623", "da914", "da916", "da917"]

run_type = ["Ctrl", "Ramp-Up 1", "Ramp-Up 2", "Ramp-Up 3", "Ramp-Up 4", "Hist 1", "Hist 2", "Hist 3", "Hist 4"]

runs = dict(zip(id, run_type)) 

count = 0

####################################################################################

# Read ice sheet data

print("Getting ice sheet data...")

icesheet_d = {}

for i in id:

    print(f"Working on {i}: {runs[i]}")

    AIS_stats = pd.read_csv(f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/new_{i}_AIS_diagnostics.csv")

    if i == "cs568":    
         AIS_stats.time = AIS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)-100
    
    else:
        AIS_stats.time = AIS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)
        
    AIS_grounded_SMB = AIS_stats[(AIS_stats['region'] == 'grounded') & (AIS_stats['quantity'] == 'SMB')]
    AIS_floating_SMB = AIS_stats[(AIS_stats['region'] == 'floating') & (AIS_stats['quantity'] == 'SMB')]
    AIS_floating_BMB = AIS_stats[(AIS_stats['region'] == 'floating') & (AIS_stats['quantity'] == 'BMB')]
    AIS_GL_discharge = AIS_stats[(AIS_stats['region'] == 'grounded') & (AIS_stats['quantity'] == 'discharge')]
    AIS_GL_flux = AIS_stats[(AIS_stats['region'] == 'grounded') & (AIS_stats['quantity'] == 'flux')]
    AIS_grounded_vol = AIS_stats[(AIS_stats['region'] == 'grounded') & (AIS_stats['quantity'] == 'volume')]
    AIS_floating_vol = AIS_stats[(AIS_stats['region'] == 'floating') & (AIS_stats['quantity'] == 'volume')]
    AIS_VAF = AIS_stats[(AIS_stats['region'] == 'entire') & (AIS_stats['quantity'] == 'volumeAbove')]

    AIS_grounded_SMB.reset_index(drop=True, inplace=True)
    AIS_floating_SMB.reset_index(drop=True, inplace=True)
    AIS_floating_BMB.reset_index(drop=True, inplace=True)
    AIS_GL_discharge.reset_index(drop=True, inplace=True)
    AIS_grounded_vol.reset_index(drop=True, inplace=True)
    AIS_floating_vol.reset_index(drop=True, inplace=True)
    AIS_VAF.reset_index(drop=True, inplace=True)
    
    AIS_data = AIS_VAF
    AIS_data = AIS_data.rename(columns={'value':'VAF'})

    AIS_data.drop(['csvheader','maskNo','region', 'quantity','unit'], axis=1, inplace=True)
    
    AIS_data['groundedSMB'] = AIS_grounded_SMB['value']
    AIS_data['floatingSMB'] = AIS_floating_SMB['value']
    AIS_data['floatingBMB'] = AIS_floating_BMB['value']
    AIS_data['GLDischarge'] = AIS_GL_discharge['value']
    AIS_data['groundedVol'] = AIS_grounded_vol['value']
    AIS_data['floatingVol'] = AIS_floating_vol['value']

    AIS_data["massSLE"] = AIS_data["VAF"]*(918/(1028*3.625e14))

    icesheet_d[i] = AIS_data

####################################################################################

# Save ice sheet data

print("Saving ice sheet data to file...")

ice_save_file = open('../processed_data/historical_icesheet_data.pkl', 'wb') 
pickle.dump(icesheet_d, ice_save_file) 
ice_save_file.close()

####################################################################################