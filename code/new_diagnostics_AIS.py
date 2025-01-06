# -*- coding: utf-8 -*-
"""
Created on Thu Oct 03 10:48:31 2024

Run the updated BISICLES diagnostics tool for all plot.*.hdf5 files within a directory and use new native CSV exporting features
Chosen directory is from the command line argument
Run as: "python new_diagnostics_AIS.py [directory] [csv_file] [mask]"
@author: tom mitcham
"""

import os
import sys
import subprocess
import glob

if len(sys.argv) == 1:

    print('No directory specified. Select one by running the command "python new_diagnostics_AIS.py [directory]"')
    sys.exit()

directory =  sys.argv[1]

if not directory.endswith('/'):

    directory = directory + '/'

filetoolsPath = '/home/users/tm17544/Code/BISICLES/bisicles-uob/code/filetools/'
filetoolDiags = 'diagnostics2d.Linux.64.c++.gfortran.DEBUG.OPT.GNU.ex'

csv_file = sys.argv[2]

masked = False
maskFile = ''

if len(sys.argv) == 4 and sys.argv[3] != '0':

    masked = True
    maskFile = sys.argv[3]

if masked:

    print("Running new_diagnostics_AIS.py for directory: " + directory + " with mask: " + maskFile)

else:

    print("Running new_diagnostics_AIS.py for directory: " + directory)

count = 0

for infile in sorted(os.listdir(directory)):
    
    if infile.endswith("AIS.hdf5"):

        if count == 0:

            if masked:

                diagsCommand = filetoolsPath + filetoolDiags + ' plot_file=' + directory + infile + ' out_file=/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/processed_data/' + csv_file + ' ice_density=918.0 water_density=1028.0 h_min=1.0e-3 mask_file=' + maskFile + ' mask_no_start=0 mask_no_end=16'
        
            else:

                diagsCommand = filetoolsPath + filetoolDiags + ' plot_file=' + directory + infile + ' out_file=/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/processed_data/' + csv_file + ' ice_density=918.0 water_density=1028.0 h_min=1.0e-3'
        
        else:

            if masked:
                    
                diagsCommand = filetoolsPath + filetoolDiags + ' plot_file=' + directory + infile + ' out_file=/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/processed_data/' + csv_file + ' -append ice_density=918.0 water_density=1028.0 h_min=1.0e-3 mask_file=' + maskFile + ' mask_no_start=0 mask_no_end=16'

            else:
                
                diagsCommand = filetoolsPath + filetoolDiags + ' plot_file=' + directory + infile + ' out_file=/home/users/tm17544/gws_terrafirma/TerraFIRMA_overshoots/processed_data/' + csv_file + ' -append ice_density=918.0 water_density=1028.0 h_min=1.0e-3'
        
        count = count + 1
        
        print("Running diagnostics for file: " + infile)
        
        diagsOutput = subprocess.check_output(diagsCommand,shell=True)

if count == 0:
    print("No plot.*.hdf5 files found")
else:
    print(str(count) + " plot.*.hdf5 files found. Created diagnostics file " + csv_file)
