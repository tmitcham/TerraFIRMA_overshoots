####################################################################################
# Imports

import cf
import pandas as pd
import os
import fnmatch
import numpy as np
import pickle
import argparse

####################################################################################

# Options for the script from command line arguments

# Set up the argument parser
parser = argparse.ArgumentParser(description="Process TerraFIRMA diagnostics with various configurations.")

# Add command-line arguments
parser.add_argument("--icesheet", choices=["AIS", "GrIS"], default="AIS",
                    help='Select the icesheet: "AIS" for Antarctic Ice Sheet, "GrIS" for Greenland Ice Sheet.')
parser.add_argument("--suite_set", choices=["overshoots", "historical_rampups"], default="overshoots",
                    help='Select the suite set: "overshoots" or "historical_rampups".')
parser.add_argument("--process_atmos_data", type=bool, default=True,
                    help="Process atmospheric data (True/False).")
parser.add_argument("--process_icesheet_data", type=bool, default=True,
                    help="Process icesheet data (True/False).")
parser.add_argument("--basin_mask", type=bool, default=False,
                    help="Apply basin mask (True/False).")

# Parse the arguments
args = parser.parse_args()

# Access the arguments
icesheet = args.icesheet
suite_set = args.suite_set
process_atmos_data = args.process_atmos_data
process_icesheet_data = args.process_icesheet_data
basin_mask = args.basin_mask

# Example printout of the arguments
print("Running process_diagnostics_output.py with the following arguments:")
print(f"Ice sheet: {icesheet}")
print(f"Suite set: {suite_set}")
print(f"Process atmospheric data: {process_atmos_data}")
print(f"Process ice sheet data: {process_icesheet_data}")
print(f"Basin mask: {basin_mask}")

####################################################################################

# Define id based on suite set
if suite_set == "overshoots":

    id=["cs568", "cx209", "cw988", "cw989", "cw990", "cy837", "cy838", "cz374", "cz375", "cz376", "cz377", "cz378", 
        "cz834", "cz855", "cz859", "db587", "db723", "db731", "da087", "da266", "db597", "db733", "dc324", 
        "cz944", "di335", "da800", "da697", "da892", "db223", "df453", "de620", "dc251", "dc956",
        "dc051", "dc052", "dc248", "dc249", "dc565", "dd210", "dc032", "df028", "de621", "dc123", "dc130", 
        "df025", "df027", "df021", "df023", "dh541", "dh859", "de943", "de962", "de963", "dk554", "dk555", "dk556"]

elif suite_set == "historical_rampups":

    id = ["cs568", "cx209", "cw988", "cw989", "cw990", "cy623", "da914", "da916", "da917"]

# Define ice sheet data filenames
IS_filename_prefix = "/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/new_"
IS_filename_suffix = f"_{icesheet}_{'basins_' if basin_mask else ''}diagnostics.csv"

####################################################################################

# 'Process and save' or 'read' atmosphere data
if process_atmos_data:

    atmos_d = {}

    print("Processing atmosphere data...")

    for i in id:

        print(f"Working on {i}...")

        atmos_dir = f"/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/raw_data/{i}/atmos/"
        atmos_files = sorted(os.listdir(atmos_dir))
        atmos_files_matched = fnmatch.filter(atmos_files, f"{i}*.pp")
        
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

    # Save atmosphere data
    print("Saving atmosphere data to file...")

    with open(f"../processed_data/atmos_data_{suite_set}.pkl", 'wb') as atmos_save_file:
        pickle.dump(atmos_d, atmos_save_file)

else:

    # Read atmosphere data
    with open("../processed_data/atmos_data_{suite_set}.pkl", 'rb') as file:
        atmos_d = pickle.load(file)

####################################################################################

# 'Process and save' (or don't) the ice sheet data produced from diagnsotics filetool
if process_icesheet_data:

    print("Processing ice sheet data...")

    icesheet_d = {}

    for i in id:

        IS_data = {}

        print(f"Working on {i}...")

        IS_stats = pd.read_csv(f"{IS_filename_prefix}{i}{IS_filename_suffix}")

        if i == "cs568":    
            IS_stats.time = IS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)-100
        
        else:
            IS_stats.time = IS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)
            
        IS_stats["global_T"] = np.nan

        for j in atmos_d[i][:,0]:

            year = int(j+1) # because BISICLES stores data for 01/01 of following year...
            
            pos = np.where(IS_stats.time==year)

            if np.size(pos) > 0:

                IS_stats["global_T"] = IS_stats["global_T"].mask(IS_stats["time"]==year, atmos_d[i][count,1])

            else:

                print(f"Year {year} not found in AIS data for {i}")

        # Interpolate to fill NaN valures in global_delta_T
        IS_stats["global_T"].interpolate(method='linear', inplace=True)

        AIS_grounded_SMB = []
        AIS_floating_SMB = []
        AIS_floating_BMB = []
        AIS_GL_discharge = []
        AIS_grounded_vol = []
        AIS_floating_vol = []
        AIS_VAF = []
        
        for j in range(17):

            if not basin_mask and j > 0:
                break

            AIS_grounded_SMB.append(IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'grounded') & (IS_stats['quantity'] == 'SMB')])
            AIS_floating_SMB.append(IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'floating') & (IS_stats['quantity'] == 'SMB')])
            AIS_floating_BMB.append(IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'floating') & (IS_stats['quantity'] == 'BMB')])
            AIS_GL_discharge.append(IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'grounded') & (IS_stats['quantity'] == 'discharge')])
            AIS_grounded_vol.append(IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'grounded') & (IS_stats['quantity'] == 'volume')])
            AIS_floating_vol.append(IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'floating') & (IS_stats['quantity'] == 'volume')])
            AIS_VAF.append(IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'entire') & (IS_stats['quantity'] == 'volumeAbove')])

            AIS_grounded_SMB[j].reset_index(drop=True, inplace=True)
            AIS_floating_SMB[j].reset_index(drop=True, inplace=True)
            AIS_floating_BMB[j].reset_index(drop=True, inplace=True)
            AIS_GL_discharge[j].reset_index(drop=True, inplace=True)
            AIS_grounded_vol[j].reset_index(drop=True, inplace=True)
            AIS_floating_vol[j].reset_index(drop=True, inplace=True)
            AIS_VAF[j].reset_index(drop=True, inplace=True)

            IS_data[j] = pd.concat([AIS_grounded_SMB[j], AIS_floating_SMB[j], AIS_floating_BMB[j], AIS_GL_discharge[j], AIS_grounded_vol[j], AIS_floating_vol[j], AIS_VAF[j]], axis=1)
        
        icesheet_d[i] = IS_data

    # Correct for a missing file in the dc051 suite (TODO: find a better way to do this)
    icesheet_d["dc051"][0] = icesheet_d["dc051"][0].reindex(icesheet_d["dc051"][0].index.tolist() + [186.5])
    icesheet_d["dc051"][0] = icesheet_d["dc051"][0].sort_index().reset_index(drop=True)
    icesheet_d["dc051"][0].iloc[:,[2,8,61]] = icesheet_d["dc051"][0].iloc[:,[2,8,61]].interpolate(method='linear')

    # Save ice sheet data
    print("Saving ice sheet data to file...")

    with open(f"../processed_data/icesheet_data_{suite_set}_{'basins' if basin_mask else ''}.pkl", 'wb') as icesheet_save_file:
        pickle.dump(icesheet_d, icesheet_save_file)

