####################################################################################

import os
import argparse
import subprocess

####################################################################################

# Extract the surface and basal thickness source from UKESM output files and save them to a series of hdf5 files that can be read into BISICLES

# Executable
EXTRACT_EXEC="/gws/nopw/j04/terrafirma/tm17544/BISICLES_filetools/extract2d"

# Options
SUITE_ID="cs568"
INPUT_DIR=f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/raw_data/{SUITE_ID}/icesheet"
OUTPUT_DIR=f"/gws/nopw/j04/terrafirma/tm17544/TerraFIRMA_overshoots/processed_data/pi_surface_flux_files"
START_YEAR=1951
END_YEAR=1980

# File list
FILE_LIST = [f"{INPUT_DIR}/bisicles_{SUITE_ID}c_{year}0101_plot-AIS.hdf5" for year in range(START_YEAR, END_YEAR + 1)]

print(f"Processing files from {START_YEAR} to {END_YEAR} in directory: {INPUT_DIR}")

# Run the extract tool on selected files

YEAR = 1850

for input_file in FILE_LIST:

    output_file = f"{OUTPUT_DIR}/pi_AIS_SMB_BMB_{YEAR}.hdf5"

    extract_command = f"{EXTRACT_EXEC} {input_file} {output_file} activeSurfaceThicknessSource activeBasalThicknessSource"

    subprocess.check_output(extract_command, shell=True)

    YEAR += 1

    print(f"Processed {input_file} to {output_file}")

print(f"Extracted surface and basal thickness sources from {len(FILE_LIST)} files into {OUTPUT_DIR}.")