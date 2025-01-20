# -*- coding: utf-8 -*-
"""
Created on Thu Oct 03 10:48:31 2024
Modified on Fri Jan 16 2025

Run the BISICLES diagnostics tool for all plot.*.hdf5 files within a directory and export data to a csv file
Run as: "python icesheet_diagnostics.py [directory] [csv_file] [mask]"

@author: tom mitcham
"""

####################################################################################

import os
import argparse
import subprocess
import sys

####################################################################################

# Set constants
FILETOOLS_PATH = '/home/users/tm17544/Code/BISICLES/bisicles-uob/code/filetools/'
DIAGNOSTICS_EXEC = 'diagnostics2d.Linux.64.c++.gfortran.DEBUG.OPT.GNU.ex'
OUTPUT_PATH = '/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/processed_data/'
ICE_DENSITY = 918.0
WATER_DENSITY = 1028.0
H_MIN = 1.0e-3

####################################################################################

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run BISICLES diagnostics on plot.*.hdf5 files.")
    parser.add_argument("--icesheet", choices=["AIS", "GrIS"], default="AIS", help='Select the icesheet: "AIS" for Antarctic Ice Sheet, "GrIS" for Greenland Ice Sheet.')
    parser.add_argument("--directory", help="Directory containing plot.*.hdf5 files")
    parser.add_argument("--csv_file", help="Name of the output CSV file")
    parser.add_argument("--mask", nargs="?", default=0, help="Optional mask file (default: 0 for no mask)")
    parser.add_argument("--mask_no_start", type=int, default=0, help="ID of the first subdomain to calculate - 0 is the entire domain (default: 0)")
    parser.add_argument("--mask_no_end", type=int, default=16, help="ID of the last subdomain to calculate (default: 16)")
    return parser.parse_args()

def validate_directory(directory):
    """Validate that the provided directory exists."""
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory does not exist: {directory}")
    return os.path.abspath(directory)

def construct_command(plot_file, csv_file, append=False, mask_file=None, mask_no_start=0, mask_no_end=16):
    """Construct the diagnostics command."""
    cmd = f"{os.path.join(FILETOOLS_PATH, DIAGNOSTICS_EXEC)} plot_file={plot_file} out_file={os.path.join(OUTPUT_PATH, csv_file)}"
    if append:
        cmd += " -append"
    cmd += f" ice_density={ICE_DENSITY} water_density={WATER_DENSITY} h_min={H_MIN}"
    if mask_file:
        cmd += f" mask_file={mask_file} mask_no_start={mask_no_start} mask_no_end={mask_no_end}"
    return cmd

####################################################################################

args = parse_arguments()

# Validate and process directory
icesheet = args.icesheet
directory = validate_directory(args.directory)
csv_file = args.csv_file
mask_file = None if args.mask == "0" else args.mask
masked = mask_file is not None
mask_no_start = args.mask_no_start
mask_no_end = args.mask_no_end

print(f"Running icesheet diagnostics in directory: {directory}")
if masked:
    print(f"Using mask file: {mask_file}")

# Process files
count = 0
for infile in sorted(os.listdir(directory)):
    
    if icesheet == "AIS" and infile.endswith("AIS.hdf5"):
        plot_file = os.path.join(directory, infile)

    elif icesheet == "GrIS" and infile.endswith("GrIS.hdf5"):
        plot_file = os.path.join(directory, infile)
        
    append = count > 0
    diags_command = construct_command(plot_file, csv_file, append=append, mask_file=mask_file)

    print(f"Running diagnostics for file: {infile}")
    try:
        subprocess.check_output(diags_command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running diagnostics for {infile}: {e}")
        continue  # Skip to the next file
    count += 1

# Summary
if count == 0:
    print("No plot.*.hdf5 files found in the directory.")
else:
    print(f"{count} plot.*.hdf5 files processed. Diagnostics written to {csv_file}.")