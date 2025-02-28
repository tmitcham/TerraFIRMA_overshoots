####################################################################################
# Imports

import cf
import pandas as pd
import os
import fnmatch
import numpy as np
import pickle
import xarray as xr

####################################################################################

ICE_DENSITY = 918.0 # As defined in BISICLES input files
OCEAN_DENSITY = 1028.0
OCEAN_AREA = 3.625e14 # as in Gregory et al. 2019 (https://doi.org/10.1007/s10712-019-09525-z)

# Following simplest calculation from Goelzer et al. 2020 (https://doi.org/10.5194/tc-14-833-2020)
def vaf_to_sle(vaf):
    return (vaf/OCEAN_AREA)*(ICE_DENSITY/OCEAN_DENSITY)

####################################################################################

# Options for the script
icesheet = "AIS" # Options: "AIS" or "GrIS"
suite_set = "overshoots" # Options: "overshoots", "historical_rampups"
process_atmos_data = False # Options: True, False
process_icesheet_data = True # Options: True, False
data_to_netcdf = False # Options: True, False
basin_mask = True # Options: True, False
basins_for_netcdf = [8,15] # Options: any from 0-16 - 0 (whole AIS), 8 (Ross), 15 (Filchner-Ronne)

# Printout of the options chosen
print("Running process_diagnostics_output.py with the following arguments:")
print(f"Ice sheet: {icesheet}")
print(f"Suite set: {suite_set}")
print(f"Process atmospheric data: {process_atmos_data}")
print(f"Process ice sheet data: {process_icesheet_data}")
print(f"Basin mask: {basin_mask}")
print(f"Save to NetCDF: {data_to_netcdf}")

####################################################################################

# Define id based on suite set
if suite_set == "overshoots":
    id=["cs568", "cx209", "cw988", "cw989", "cw990", "cy837", "cy838", "cz374", "cz375", "cz376", 
        "cz377", "cz378", "cz834", "cz855", "cz859", "db587", "db723", "db731", "da087", "da266", 
        "db597", "db733", "dc324", "di335", "da800", "da697", "da892", "db223", "df453", 
        "de620", "dc251", "dc051", "dc052", "dc248", "dc249", "dc565", "dd210", 
        "df028", "de621", "dc123", "dc130", "df025", "df027", "df021", "df023", "dh541", "dh859", 
        "dg093", "dg094", "dg095", "de943", "de962", "de963", "dm357", "dm358", "dm359"]

elif suite_set == "historical_rampups":
    id = ["cs568", "cx209", "cw988", "cw989", "cw990", "cy623", "da914", "da916", "da917"]

# Define ice sheet data filenames
IS_filename_prefix = "/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/"
IS_filename_suffix = f"_{icesheet}_diagnostics{'_masked' if basin_mask else ''}.csv"

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

    # Save atmosphere data
    print("Saving atmosphere data to file...")

    with open(f"../processed_data/atmos_data_{suite_set}.pkl", 'wb') as atmos_save_file:
        pickle.dump(atmos_d, atmos_save_file)

####################################################################################

# 'Process and save' (or don't) the ice sheet data produced from diagnsotics filetool
if process_icesheet_data:

    print("Processing ice sheet data...")

    icesheet_d = {}

    for i in id:

        IS_data = {}

        print(f"Working on {i}...")

        file_to_read = f"{IS_filename_prefix}{i}{IS_filename_suffix}"

        if not os.path.exists(file_to_read):
            print(f"File {file_to_read} does not exist. Skipping...")
            continue
        
        IS_stats = pd.read_csv(file_to_read)

        if i == "cs568":    
            IS_stats.time = IS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)-100
        
        else:
            IS_stats.time = IS_stats.apply(lambda x: int(x.filename[97:101]), axis=1)

        grounded_SMB = []
        floating_SMB = []
        floating_BMB = []
        GL_discharge = []
        grounded_vol = []
        floating_vol = []
        VAF = []
        SLE = []
        
        for j in range(17):

            if not basin_mask and j > 0:
                break

            file_time_T = IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'grounded') & (IS_stats['quantity'] == 'SMB')][['filename','time']]
            
            grounded_SMB = IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'grounded') & (IS_stats['quantity'] == 'SMB')][['value']]
            floating_SMB = IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'floating') & (IS_stats['quantity'] == 'SMB')][['value']]
            floating_BMB = IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'floating') & (IS_stats['quantity'] == 'BMB')][['value']]
            GL_discharge = IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'grounded') & (IS_stats['quantity'] == 'discharge')][['value']]
            grounded_vol = IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'grounded') & (IS_stats['quantity'] == 'volume')][['value']]
            floating_vol = IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'floating') & (IS_stats['quantity'] == 'volume')][['value']]
            VAF = IS_stats[(IS_stats['maskNo'] == j) & (IS_stats['region'] == 'entire') & (IS_stats['quantity'] == 'volumeAbove')][['value']]
            SLE = vaf_to_sle(VAF)

            grounded_SMB.columns = ['grounded_SMB']
            floating_SMB.columns = ['floating_SMB']
            floating_BMB.columns = ['floating_BMB']
            GL_discharge.columns = ['GL_discharge']
            grounded_vol.columns = ['grounded_vol']
            floating_vol.columns = ['floating_vol']
            VAF.columns = ['VAF']
            SLE.columns = ['SLE']

            IS_data[j] = pd.concat([
                file_time_T.reset_index(drop=True),
                grounded_SMB.reset_index(drop=True),
                floating_SMB.reset_index(drop=True),
                floating_BMB.reset_index(drop=True),
                GL_discharge.reset_index(drop=True),
                grounded_vol.reset_index(drop=True),
                floating_vol.reset_index(drop=True),
                VAF.reset_index(drop=True),
                SLE.reset_index(drop=True)],
                axis=1)

            IS_data = IS_data[j].sort_values(by='time').reset_index(drop=True)

        icesheet_d[i] = IS_data

    # Save ice sheet data
    print("Saving ice sheet data to file...")

    with open(f"../processed_data/{icesheet}_data_{suite_set}{'_masked' if basin_mask else ''}.pkl", 'wb') as icesheet_save_file:
        pickle.dump(icesheet_d, icesheet_save_file)

####################################################################################

# Access VAF data from the Ross and the Filchner-Ronne basins 
# and convert to an xarray dataset and save in NetCDF format

if data_to_netcdf:

    if not process_icesheet_data:
        
        # Read ice sheet data
        with open(f"../processed_data/{icesheet}_data_{suite_set}_{'masked' if basin_mask else ''}.pkl", 'rb') as file:
            icesheet_d = pickle.load(file)

    print("Saving selected data to netCDF...")

    for i in id:

        IS_data = icesheet_d[i]

        time = IS_data[0].time

        vaf_ds = xr.Dataset(coords={'time': time})

        vaf_ds.attrs = {
            "title": "Ross and Filchner-Ronne VAF and SLE timeseries",
            "description": f"Ice volume above flotation and sea level equivalent timeseries for the basins that feed into the Ross and Filchner-Ronne ice shelves in Antarctica. Data from the TerraFIRMA overshoots simulation with suite id u-{i}",
            "creator": "Tom Mitcham",
            "institution": "CPOM, University of Bristol",
            "comment": "This is just a provisional .nc file for testing in Kailtin's plotting workflow. Processing of the ice sheet data is continuing and this file will be updated before finalising plots and analysis."
        }

        for j in basins_for_netcdf:

            vaf = xr.DataArray(IS_data[j].VAF, dims='time', coords={'time': time})
            sle = xr.DataArray(IS_data[j].SLE, dims='time', coords={'time': time})

            data_label_vaf = "ross_vaf" if j == 8 else "filchner_ronne_vaf"
            data_label_sle = "ross_sle" if j == 8 else "filchner_ronne_sle"

            data_desc = "Ross" if j == 8 else "Filchner-Ronne"

            vaf_ds[data_label_vaf] = vaf
            vaf_ds[data_label_sle] = sle

            vaf_ds[data_label_vaf].attrs = {
                "long_name": f"Ice volume above flotation in the {data_desc} basin",
                "units": "m$^{3}"
            }

            vaf_ds[data_label_sle].attrs = {
                "long_name": f"Sea level equivalent of the ice volume above flotation in the {data_desc} basin",
                "units": "m"
            }
    
        vaf_ds.to_netcdf(f"../processed_data/netcdf_files/vaf_{i}_timeseries.nc")

        print(f"NetCDF file saved for {i}")

####################################################################################
    
