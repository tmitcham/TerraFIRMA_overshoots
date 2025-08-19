####################################################################################

import os
import argparse
import subprocess

####################################################################################

# Extract the surface and basal thickness source from UKESM output files and save them to a series of hdf5 files that can be read into BISICLES

# Executables
EXTRACT_EXEC="/gws/nopw/j04/terrafirma/tm17544/BISICLES_filetools/extract2d"
FLATTEN_EXEC="/gws/nopw/j04/terrafirma/tm17544/BISICLES_filetools/flatten2d"

# Options
#="cs568"
SUITE_ID="cy623"
INPUT_DIR=f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/raw_data/{SUITE_ID}/icesheet"
#OUTPUT_DIR=f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/pi_surface_flux_files"
OUTPUT_DIR=f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/hist_surface_flux_files"

START_YEAR=1851

START_YEAR=1851
END_YEAR=2014

FLATTEN_LEVEL=3

# File list
FILE_LIST = [f"{INPUT_DIR}/bisicles_{SUITE_ID}c_{year}0101_plot-AIS.hdf5" for year in range(START_YEAR, END_YEAR + 1)]

print(f"Processing files from {START_YEAR} to {END_YEAR} in directory: {INPUT_DIR}")

# Run the extract tool on selected files

YEAR = 1850

for input_file in FILE_LIST:

    #extract_output_file = f"{OUTPUT_DIR}/pi_AIS_SMB_BMB_{YEAR}.hdf5"
    extract_output_file = f"{OUTPUT_DIR}/hist_AIS_SMB_BMB_{YEAR}.hdf5"

    extract_command = f"{EXTRACT_EXEC} {input_file} {extract_output_file} activeSurfaceThicknessSource activeBasalThicknessSource"

    subprocess.check_output(extract_command, shell=True)

    print(f"Extracted surface and basal thickness sources from {input_file} to {extract_output_file}")

    #flatten_output_file = f"{OUTPUT_DIR}/pi_AIS_SMB_BMB_{YEAR}_1km.hdf5"
    flatten_output_file = f"{OUTPUT_DIR}/hist_AIS_SMB_BMB_{YEAR}_1km.hdf5"

    flatten_command = f"{FLATTEN_EXEC} {extract_output_file} {flatten_output_file} {FLATTEN_LEVEL}"

    subprocess.check_output(flatten_command, shell=True)

    YEAR += 1

    print(f"Flattened output saved to {flatten_output_file} at {(8/(2**FLATTEN_LEVEL))}km resolution.")

print(f"Extracted surface and basal thickness sources from {len(FILE_LIST)} files into {OUTPUT_DIR}.")